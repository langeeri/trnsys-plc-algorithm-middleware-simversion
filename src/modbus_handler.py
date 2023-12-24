
import logging
from pymodbus.client import ModbusTcpClient
from pymodbus.payload import BinaryPayloadBuilder, Endian
from typing import Dict, List, Union, Optional
from main_config import SIMULATION_MODEL


class ModbusServer:
    """
    Represents a Modbus modbus_server with methods for connecting, reading, and writing data.

    Parameters
    ----------
    host : str
        The IP address or hostname of the Modbus modbus_server.
    port : int
        The port number on which the Modbus modbus_server is listening.
    rw_registers : List[int]
        List of Modbus registers for read-write operations.
    input_indexes : List[int]
        List of input indexes for the modbus_server.
    r_registers : List[int]
        List of Modbus registers for read-only operations.

    Attributes
    ----------
    host : str
        The IP address or hostname of the Modbus modbus_server.
    port : int
        The port number on which the Modbus modbus_server is listening.
    rw_registers : List[int]
        List of Modbus registers for read-write operations.
    input_indexes : List[int]
        List of input indexes for the modbus_server.
    r_registers : List[int]
        List of Modbus registers for read-only operations.
    client : ModbusTcpClient
        The Modbus TCP client used to communicate with the modbus_server.

    Methods
    -------
    connect()
        Establish a connection to the Modbus modbus_server.
    write_inputs_modbus(inputs)
        Write inputs to the Modbus modbus_server.
    read_outputs_modbus(TRNData)
        Read outputs from the Modbus modbus_server and update TRNData.
    close_connection_modbus()
        Close the connection to the Modbus modbus_server.

    """

    def __init__(self, host: str, port: int, rw_registers: Optional[List[int]], input_indexes: List[int], r_registers: Optional[List[int]]):
        self.host = host
        self.port = port
        self.rw_registers = rw_registers
        self.input_indexes = input_indexes
        self.r_registers = r_registers
        self.client = None

    def open_connection_modbus(self)-> None:
        """
        Establish a connection to the Modbus modbus_server.

        Raises
        ------
        Exception
            If an error occurs during the connection.

        """

        try:
            self.client = ModbusTcpClient(host=self.host, port=self.port)
        except Exception as e:
            logging.error(f"Error initializing Modbus client for {self.host}:{self.port}: {e}")
            raise

    def write_inputs_modbus(self, inputs: List[Union[int, float]]) -> List[Union[int, float]]:
        """
        Write inputs to the Modbus modbus_server.

        Parameters
        ----------
        inputs : List[Union[int, float]]
            List of input values to be written to the modbus_server.

        Returns
        -------
        List[Union[int, float]]
            The list of inputs that were written.

        Raises
        ------
        Exception
            If an error occurs during the write operation.

        """

        try:
            client = self.client
            builder = BinaryPayloadBuilder(byteorder=Endian.Big, wordorder=Endian.Big)
            builder.reset()

            for index, value in enumerate(inputs):
                inputConverted = int(value * 10)
                builder.add_16bit_int(inputConverted)

            payload = builder.to_registers()

            for indexRW, addressRW in enumerate(self.rw_registers):
                result = client.write_registers(addressRW-1, payload[indexRW])  # starts from 0
                if result.isError():
                    logging.error(f"Error writing to PLC register for {self.host}:{self.port}: {result}")
                else:
                    logging.info(f"Successfully wrote {inputs[indexRW]} to PLC register {addressRW} for {self.host}:{self.port}")

            return inputs

        except Exception as e:
            logging.error(f"Error writing to PLC register for {self.host}:{self.port}: {e}")

    def read_outputs_modbus(self, TRNData: Dict[str, Dict[str, Union[int, float]]]) -> None:
        """
        Read outputs from the Modbus modbus_server and update TRNData.

        Parameters
        ----------
        TRNData : Dict[str, Dict[str, Union[int, float]]]
            A dictionary containing TRNSYS simulation model data.

        Raises
        ------
        Exception
            If an error occurs during the read operation.

        """

        arrayOfResponses = []
        
        try: 
            for addressR in self.r_registers:
                responseR = self.client.read_holding_registers(addressR-1)
                registerValue = responseR.getRegister(0)
                arrayOfResponses.append(registerValue)

            # Send response to TRNSYS.
            for indexR, addressR in enumerate(self.r_registers):
                TRNData[SIMULATION_MODEL]["outputs"][indexR] = arrayOfResponses[indexR]

        except Exception as e:
            logging.error(f"Error writing to TRNSYS from {self.host}:{self.port}: {e}")

    def close_connection_modbus(self) -> None:
        """
        Close the connection to the Modbus modbus_server.

        Raises
        ------
        Exception
            If an error occurs during the connection closure.

        """
        
        try:
            if self.client:
                self.client.close()
        except Exception as e:
            logging.error(f"Error closing Modbus connection for {self.host}:{self.port}: {e}")

def define_modbus_servers(modbus_servers_configs: List[Dict[str, Union[str, int, List[int], int, List[int]]]]) -> List[ModbusServer]:
    """
    Initialize Modbus modbus_servers based on the provided configuration.

    Parameters
    ----------
    modbus_servers_configs : List[Dict[str, Union[str, int, List[int], int, List[int]]]]
        List of dictionaries containing configuration information for Modbus modbus_servers.

    Returns
    -------
    List[ModbusServer]
        List of initialized ModbusServer instances.

    """

    modbus_servers = []
    for config in modbus_servers_configs:
        modbus_server = ModbusServer(
            host=config['host'],
            port=config['port'],
            rw_registers=config['rw_registers'],
            input_indexes=config['input_indexes'],
            r_registers=config['r_registers']
        )
        modbus_servers.append(modbus_server)
    return modbus_servers