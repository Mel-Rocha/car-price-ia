import csv

class Config:
    valid_models = set()
    valid_brands = set()

    @classmethod
    def load_valid_models(cls, file_path: str):
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                cls.valid_models.add(row[0])

    @classmethod
    def load_valid_brands(cls, file_path: str):
        with open(file_path, newline='') as csvfile:
            reader = csv.reader(csvfile)
            for row in reader:
                cls.valid_brands.add(row[0])

config = Config()