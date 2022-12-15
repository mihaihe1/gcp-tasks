import apache_beam as beam
import argparse
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions

SCHEMA = ",".join(
    [
        "field1:STRING",
        "field2:INTEGER",
        "field3:FLOAT64",
        "field4:TIMESTAMP",
    ]
)

ERROR_SCHEMA = ",".join(
    [
        "field1:STRING",
        "field2:TIMESTAMP",
    ]
)


class Parser(beam.DoFn):
    ERROR_TAG = 'error'

    def process(self, line):
        try:
            data_row = # parse json message according to table schema
            yield data_row
        except Exception as error:
            error_row = # parse json message according to ERRORS table schema
            yield beam.pvalue.TaggedOutput(self.ERROR_TAG, error_row)


def run(options, input_subscription, output_table, output_error_table):

    with beam.Pipeline(options=options) as pipeline:
        rows, error_rows = \
            (pipeline | 'Read from PubSub' >> beam.io.ReadFromPubSub(subscription=input_subscription)
             | 'Parse JSON messages' >> beam.ParDo(Parser()).with_outputs(Parser.ERROR_TAG,
                                                                                main='rows')
             )

        _ = (rows | 'Write data to BigQuery'
             >> beam.io.WriteToBigQuery(output_table,
                                        create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
                                        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                                        schema=SCHEMA
                                        )
             )

        _ = (error_rows | 'Write errors to BigQuery'
             >> beam.io.WriteToBigQuery(output_error_table,
                                        create_disposition=beam.io.BigQueryDisposition.CREATE_NEVER,
                                        write_disposition=beam.io.BigQueryDisposition.WRITE_APPEND,
                                        schema=ERROR_SCHEMA
                                        )
             )


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--input_subscription', required=True,
        help='Input PubSub subscription of the form "/subscriptions/<PROJECT>/<SUBSCRIPTION>".')
    parser.add_argument(
        '--output_table', required=True,
        help='Output BigQuery table for data')
    parser.add_argument(
        '--output_error_table', required=True,
        help='Output BigQuery table for errors')
    known_args, pipeline_args = parser.parse_known_args()
    pipeline_options = PipelineOptions(pipeline_args)
    pipeline_options.view_as(SetupOptions).save_main_session = True
    run(pipeline_options, known_args.input_subscription, known_args.output_table, known_args.output_error_table)
