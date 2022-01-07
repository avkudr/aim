from aim.storage.structured.entities import \
    ObjectFactory, Run, Tag, Experiment,\
    RunCollection, ExperimentCollection, TagCollection
from aim.storage.structured.sql_engine.entities import ModelMappedRun, ModelMappedExperiment, ModelMappedTag


class ModelMappedFactory(ObjectFactory):
    def __init__(self):
        self._session_depth = 0
        self._session = None

    @staticmethod
    def run_cls():
        return ModelMappedRun

    @staticmethod
    def experiment_cls():
        return ModelMappedExperiment

    @staticmethod
    def tag_cls():
        return ModelMappedTag

    def runs(self) -> RunCollection:
        return ModelMappedRun.all(session=self._session or self.get_session())

    def search_runs(self, term: str) -> RunCollection:
        return ModelMappedRun.search(term, session=self._session or self.get_session())

    def find_run(self, _id: str) -> Run:
        return ModelMappedRun.find(_id, session=self._session or self.get_session())

    def find_runs(self, ids: list[str]) -> list[Run]:
        return ModelMappedRun.find_some(ids, session=self._session or self.get_session())

    def create_run(self, runhash: str) -> Run:
        return ModelMappedRun.from_hash(runhash, session=self._session or self.get_session())

    def delete_run(self, runhash: str) -> bool:
        return ModelMappedRun.delete_run(runhash, session=self._session or self.get_session())

    def experiments(self) -> ExperimentCollection:
        return ModelMappedExperiment.all(session=self._session or self.get_session())

    def search_experiments(self, term: str) -> ExperimentCollection:
        return ModelMappedExperiment.search(term, session=self._session or self.get_session())

    def find_experiment(self, _id: str) -> Experiment:
        return ModelMappedExperiment.find(_id, session=self._session or self.get_session())

    def create_experiment(self, name: str) -> Experiment:
        return ModelMappedExperiment.from_name(name, session=self._session or self.get_session())

    def tags(self) -> TagCollection:
        return ModelMappedTag.all(session=self._session or self.get_session())

    def search_tags(self, term: str) -> TagCollection:
        return ModelMappedTag.search(term, session=self._session or self.get_session())

    def find_tag(self, _id: str) -> Tag:
        return ModelMappedTag.find(_id, session=self._session or self.get_session())

    def create_tag(self, name: str) -> Tag:
        return ModelMappedTag.from_name(name, session=self._session or self.get_session())

    def delete_tag(self, _id: str) -> bool:
        return ModelMappedTag.delete(_id, session=self._session or self.get_session())

    def get_session(self, autocommit=True):
        raise NotImplementedError

    def __enter__(self):
        if self._session_depth == 0:
            assert self._session is None
            self._session = self.get_session(autocommit=False)
        self._session_depth += 1
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        assert self._session_depth > 0
        self._session_depth -= 1
        if self._session_depth == 0:
            if exc_type is None:
                self._session.commit()
            else:
                self._session.rollback()
            self._session = None
