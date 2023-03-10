import apache_beam as beam
import argparse
from apache_beam.options.pipeline_options import PipelineOptions
from apache_beam.options.pipeline_options import SetupOptions
from datetime import datetime
import json
import logging
import datetime
import time

logging.basicConfig(level=logging.INFO)

SCHEMA = ",".join(
    [
        "message:STRING",
        "number_int:INTEGER",
        "number_float:FLOAT",
        "timestamp:TIMESTAMP",
    ]
)

ERROR_SCHEMA = ",".join(
    [
        "err_message:STRING",
        "timestamp:TIMESTAMP",
    ]
)


class Parser(beam.DoFn):
    ERROR_TAG = 'error'

    def process(self, line):
        try:
            row = json.loads(line.decode("utf-8"))

            logging.info(f"MESSAGE, {row}")
            yield {
                "message": row["message"],
                "number_int": int(row["number_int"]),
                "number_float": float(row["number_float"]),
                "timestamp": row["timestamp"]
            }
        except Exception as error:
            logging.info("ERROR")
            now = datetime.datetime.utcnow()
            ts = now.strftime('%Y-%m-%d %H:%M:%S')
            error_row = {"err_message": str(error), "timestamp": ts}
            time.sleep(1)
            yield beam.pvalue.TaggedOutput(self.ERROR_TAG, error_row)


# {"message", "test", "number_int":"1", "number_float":"2", "timestamp":"2022-12-15"}
# {"message", "test", "number_int":"1", "number_float":"2"}
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


# if __name__ == '__main__':
parser = argparse.ArgumentParser()
parser.add_argument(
    '--input_subscription', default="/subscriptions/task-cf-370908/dataflow-topic-sub", required=True,
    help='Input PubSub subscription of the form "/subscriptions/<PROJECT>/<SUBSCRIPTION>".')
parser.add_argument(
    '--output_table', default="task-cf-370908.dataflow.messages", required=True,
    help='Output BigQuery table for data')
parser.add_argument(
    '--output_error_table', default="task-cf-370908.dataflow.errors", required=True,
    help='Output BigQuery table for errors')
known_args, pipeline_args = parser.parse_known_args()
pipeline_options = PipelineOptions(pipeline_args)
pipeline_options.view_as(SetupOptions).save_main_session = True
run(pipeline_options, known_args.input_subscription, known_args.output_table, known_args.output_error_table)
