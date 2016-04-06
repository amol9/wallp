
from asq.initiators import query

from ..db.model.image_trace import ImageTrace
from ..util import log
from ..util.printer import printer


class Trace:

	def __init__(self):
		self._steps = []
		self._step = 1


	def add_step(self, name, data, log_debug=True, print_step=True, overwrite=False):
		if not overwrite:
			self._steps.append(ImageTrace(step=self._step, name=name, data=data))
		else:
			step = next(iter(query(self._steps).where(lambda s : s.name == name)), None)
			if step is not None:
				step.data = data
			else:
				self._steps.append(ImageTrace(step=self._step, name=name, data=data))

		if log_debug:
			log.debug(name + (': ' + data) if data is not None else '')

		if print_step:
			printer.printf(name, data if data is not None else '')

		self._step += 1


	def add_trace_from(self, service):
		self._steps += service.steps


	def get_steps(self):
		return self._steps


	steps = property(get_steps)

