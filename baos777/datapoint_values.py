import logging
from dataclasses import dataclass, field
from typing import Any


DPT1_VALUES = {"on": True, "off": False}
DPT3_VALUES = {"increase": True, "decrease": False, "step code": 5}


@dataclass
class DatapointValue:
    datapoint_format: str
    value: str
    formatted_value: Any = field(init=False)

    def __post_init__(self):
        self._set_formatted_value()

    def _set_formatted_value(self):
        _set_method = f"_set_{self.datapoint_format.lower()}"

        if hasattr(self, _set_method):
            _datapoint_value_setter = getattr(self, _set_method)
            if callable(_datapoint_value_setter):
                _datapoint_value_setter()

    def _set_dpt1(self):
        self.formatted_value = DPT1_VALUES.get(self.value)

    def _set_dpt2(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt3(self):
        control = DPT3_VALUES.get(self.value)
        step_code = DPT3_VALUES.get("step code")
        self.formatted_value = {"Control": control, "StepCode": step_code}

    def _set_dpt4(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt5(self):
        scaling = round(float(self.value))  # 0...100%
        percent_u8 = int(scaling) * 255 / 100  # 0...255%
        self.formatted_value = int(round(percent_u8))

    def _set_dpt6(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt7(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt8(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt9(self):
        self.formatted_value = float(self.value)

    def _set_dpt10(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt11(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt12(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt13(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt14(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt16(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt18(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt20(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None

    def _set_dpt232(self):
        logging.info(f"Datapoint {self.datapoint_format} not implemented")
        self.formatted_value = None
