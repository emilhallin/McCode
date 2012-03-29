from app import db
from sqlalchemy import DDL
from json import dumps, loads
from datetime import datetime


class Job(db.Model):
    ''' A job specifying the simuation to run and its status '''
    id      = db.Column(db.String(38), primary_key=True)
    seed    = db.Column(db.Integer)
    samples = db.Column(db.Integer)
    sim_id  = db.Column(db.Integer, db.ForeignKey('simulation.id'))
    params  = db.relationship('ParamValue', backref='job')
    created = db.Column(db.DateTime(timezone=False), index=True)

    def __init__(self, id, seed, samples, sim):
        self.id = id
        self.seed = seed
        self.samples = samples
        self.sim_id = sim.id
        self.created = datetime.now()


class Simulation(db.Model):
    ''' A simulation '''
    id     = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name   = db.Column(db.String(64))
    params = db.relationship('ParamDefault', backref='sim')
    jobs   = db.relationship('Job', backref='sim')
    runs   = db.relationship('SimRun', backref='sim')

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return self.name


class SimRun(db.Model):
    ''' A particular run of a simulation (configured by Job) '''
    id     = db.Column(db.String(64), primary_key=True)
    job_id = db.Column(db.String(38), db.ForeignKey('job.id'))
    sim_id = db.Column(db.Integer, db.ForeignKey('simulation.id'))
    status = db.Column(db.String(32), index=True)
    str_params = db.Column(db.String())
    str_result = db.Column(db.String())
    created = db.Column(db.DateTime(timezone=False), index=True)

    def __init__(self, job, sim, params):
        self.id     = job.id + "__" + str(datetime.now()).replace(' ', '_')
        self.job_id = job.id
        self.sim_id = sim.id
        self.status = "waiting"
        self.params = params
        self.result = ""
        self.created = datetime.now()

    @property
    def params(self):
        return loads(self.str_params)
    @params.setter
    def params(self, p):
        self.str_params = dumps(p)

    @property
    def result(self):
        return loads(self.str_result)
    @result.setter
    def result(self, r):
        self.str_result = dumps(r)


class Param(db.Model):
    ''' A parameter '''
    id       = db.Column(db.Integer, primary_key=True)
    name     = db.Column(db.String(128))
    defaults = db.relationship('ParamDefault', backref='param')
    values   = db.relationship('ParamValue', backref='param')

    def __init__(self, name):
        self.name = name


class ParamDefault(db.Model):
    ''' A parameter default '''
    id        = db.Column(db.Integer, primary_key=True)
    param_id  = db.Column(db.Integer, db.ForeignKey('param.id'))
    str_value = db.Column(db.String(255))
    sim_id    = db.Column(db.ForeignKey('simulation.id'))

    def __init__(self, param, value, sim):
        self.param_id = param.id
        self.value    = value
        self.sim_id   = sim.id

    def simulation(self):
        return Simulation.query.filter_by(id=self.sim_id).one()

    @property
    def value(self):
        return loads(self.str_value)
    @value.setter
    def value(self, v):
        self.str_value = dumps(v)


class ParamValue(db.Model):
    ''' A parameter value tied to a specific job '''
    id        = db.Column(db.Integer, primary_key=True)
    param_id  = db.Column(db.Integer, db.ForeignKey('param.id'))
    str_value = db.Column(db.PickleType)
    job_id    = db.Column(db.ForeignKey('job.id'))

    def __init__(self, param, value, job):
        self.param_id = param.id
        self.value    = value
        self.job_id   = job.id

    def job(self):
        return

    @property
    def value(self):
        return loads(self.str_value)
    @value.setter
    def value(self, v):
        self.str_value = dumps(v)