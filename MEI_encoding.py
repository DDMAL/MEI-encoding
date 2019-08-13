from rodan.jobs.base import RodanTask
import build_mei_file as bm
import parse_classifier_table as pct
import json


class MEI_encoding(RodanTask):
    name = 'MEI Encoding'
    author = 'Tim de Reuse'
    description = 'Builds an MEI file from pitchfinding information and transcript alignment results.'
    enabled = True
    category = "Encoding"
    interactive = False

    settings = {
        'title': 'Mei Encoding Settings',
        'type': 'object',
        'required': ['Neume Component Spacing'],
        'properties': {
            'Neume Component Spacing': {
                'type': 'number',
                'default': 2.0,
                'minimum': 0.0,
                'maximum': 20.0,
                'description': 'The spacing allowed between two neume components when grouping into neumes, where 1.0 is the width of the average glyph on the page. At 0, neume components will not be merged together.',
            }
        }
    }

    input_port_types = [{
        'name': 'JSOMR',
        'resource_types': ['application/json'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }, {
        'name': 'Text Alignment JSON',
        'resource_types': ['application/json'],
        'minimum': 0,
        'maximum': 1,
        'is_list': False
    }, {
        'name': 'MEI Mapping CSV',
        'resource_types': ['text/csv'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }
    ]

    output_port_types = [{
        'name': 'MEI',
        'resource_types': ['application/mei+xml'],
        'minimum': 1,
        'maximum': 1,
        'is_list': False
    }]

    def run_my_task(self, inputs, settings, outputs):
        jsomr_path = inputs['JSOMR'][0]['resource_path']
        print('loading jsomr...')
        with open(jsomr_path, 'r') as file:
            jsomr = json.loads(file.read())

        try:
            alignment_path = inputs['Text Alignment JSON'][0]['resource_path']
        except KeyError:
            print('no text alignment given! using dummy syllables...')
            syls = None
        else:
            print('loading text alignment results..')
            with open(alignment_path, 'r') as file:
                syls = json.loads(file.read())

        print('fetching classifier...')
        classifier_table = pct.fetch_table_from_csv(inputs['MEI Mapping CSV'][0]['resource_path'])
        spacing = list(settings.values())[0]
        mei_string = bm.process(jsomr, syls, classifier_table, spacing)

        print('writing to file...s')
        outfile_path = outputs['MEI'][0]['resource_path']
        with open(outfile_path, 'w') as file:
            file.write(mei_string)

        return True
