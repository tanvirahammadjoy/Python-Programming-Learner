import json
import csv
import os

class StorageHandler:
    def __init__(self, file_format="json", filename="data"):
        self.file_format = file_format.lower()
        self.filename = f"{filename}.{self.file_format}"

    def save(self, data):
        if self.file_format == "json":
            with open(self.filename, "w") as f:
                json.dump(data, f, indent=4)

        elif self.file_format == "csv":
            if not data:
                return

            with open(self.filename, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=data[0].keys())
                writer.writeheader()
                writer.writerows(data)

    def load(self):
        if not os.path.exists(self.filename):
            return []

        try:
            if self.file_format == "json":
                with open(self.filename, "r") as f:
                    return json.load(f)

            elif self.file_format == "csv":
                with open(self.filename, "r") as f:
                    reader = csv.DictReader(f)
                    return list(reader)

        except Exception as e:
            print("Error loading file:", e)
            return []