import lmdb
import pickle
import os
import shelve

class Database:
    """
    Helps us in storing the responses and resuming the evaluation if we hit Rate Limit Error.
    """
    def __init__(self, path, model, task_num, exp_id):
        self.path = path
        self.env = lmdb.open(path)
        self.db = None
        with self.env.begin(write=True) as txn:
            name = f"model_{model}_task_{task_num}_exp_{exp_id}"
            self.db = self.env.open_db(bytes(name, encoding='utf-8'))
    
    def put(self, key, value):
        try:
            with self.env.begin(write=True, db=self.db) as txn:
                txn.put(bytes(key, 'utf-8'), pickle.dumps(value))
        except Exception as e:
            print(f"Error putting value: {e}")
    
    def get(self, key):
        try:
            with self.env.begin(write=False, db=self.db) as txn:
                value = txn.get(bytes(key, 'utf-8'))
                if value is not None:
                    return pickle.loads(value)
        except Exception as e:
            print(f"Error getting value: {e}")
        return None
    
class Shelf:
    """
    Stores successful responses.
    """
    
    def __init__(self, rootdir, run, temp):
        self.rootdir = os.path.join(rootdir, f"run_{run}_temp_{temp}")
        if not os.path.exists(self.rootdir):
            os.makedirs(self.rootdir, exist_ok=True)

        self.filename = os.path.join(self.rootdir, 'responses.db')

    def put(self, key, value):
        with shelve.open(self.filename) as db:
            db[key] = value

    def get(self, key):
        with shelve.open(self.filename) as db:
            return db[key]

    def total(self):
        with shelve.open(self.filename) as db:
            return len(db)

    def list_keys(self):
        with shelve.open(self.filename) as db:
            return list(db.keys())

    def is_exists(self, key):
        with shelve.open(self.filename) as db:
            return key in db.keys()

class ErrorShelf:
    """
    Stores questions that didn't return output in desired JSON format.
    """
    
    def __init__(self, rootdir, run, temp):
        self.rootdir = os.path.join(rootdir, f"run_{run}_temp_{temp}")
        if not os.path.exists(self.rootdir):
            os.makedirs(self.rootdir, exist_ok=True)

        self.filename = os.path.join(self.rootdir, 'failed_responses.db')

    def put(self, key, value):
        with shelve.open(self.filename) as db:
            db[key] = value

    def get(self, key):
        with shelve.open(self.filename) as db:
            return db[key]

    def total(self):
        with shelve.open(self.filename) as db:
            return len(db)

    def list_keys(self):
        with shelve.open(self.filename) as db:
            return list(db.keys())

    def list_values(self):
        with shelve.open(self.filename) as db:
            return list(db.values())

    def is_exists(self, key):
        with shelve.open(self.filename) as db:
            return key in db.keys()

    def remove(self,key):
        with shelve.open(self.filename) as db:
            del db[key]
