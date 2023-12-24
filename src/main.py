# -*- coding: utf-8 -*-

import logging
import subprocess
import time as osTime
from typing import Dict, List, Union
from modbus_handler import define_modbus_servers
from modbus_servers_config import MODBUS_SERVER_CONFIGS
from xml_server_config import XML_SUBPROCESS_CONFIG
from main_config import SIM_SLEEP, SIMULATION_MODEL, LOGGING_FILENAME

# --------------------------------------------------------------------------


def Initialization(TRNData: Dict[str, Dict[str, List[Union[int, float]]]]) -> None:
    """
    Function called at TRNSYS initialization. 
    Used to initialize modbus_servers based on the provided configuration. 

    Parameters
    ----------
    TRNData : Dict[str, Dict[str, List[Union[int, float]]]]
        A nested dictionary containing simulation data.

    Raises
    ------
    Exception
        If an error occurs during initialization, an exception is raised with
        details about the error.

    Notes
    -----
    This function initializes global variable 'modbus_servers' by connecting to modbus_servers
    based on the provided modbus_server configurations in MODBUS_SERVER_CONFIGS.

    Examples
    --------
    >>> Initialization(TRNData)

    The above example initializes modbus_servers using the configuration provided in
    'TRNData'. 

    """

    global modbus_servers, xml_server_process

    logging.basicConfig(filename=LOGGING_FILENAME, level=logging.DEBUG, format='%(asctime)s [%(levelname)s] %(message)s')

    try:
        modbus_servers_configs = MODBUS_SERVER_CONFIGS  
        modbus_servers = define_modbus_servers(modbus_servers_configs)

        for modbus_server in modbus_servers:
            modbus_server.open_connection_modbus()

    except Exception as e:
        logging.error(f"Error during initialization modbus: {e}")
        for modbus_server in modbus_servers:
            modbus_server.close_connection_modbus()

    try:
        xml_server_process = subprocess.Popen([XML_SUBPROCESS_CONFIG["interpreter"], XML_SUBPROCESS_CONFIG["filename"]])
    except Exception as e:
        logging.error(f"Error starting XML server subprocess: {e}")

    return
    

# --------------------------------------------------------------------------------

def StartTime(TRNData: Dict[str, Dict[str, List[Union[int, float]]]]) -> None:
    """
    Function called at TRNSYS starting time (not an actual time step, 
    initial values should be reported).

    Parameters
    ----------
    TRNData : Dict[str, Dict[str, List[Union[int, float]]]]
        A nested dictionary containing simulation data.

    Returns
    -------
    None
        This function does not return any value.

    """

    return

 
# --------------------------------------------------------------------------------

def Iteration(TRNData: Dict[str, Dict[str, List[Union[int, float]]]]) -> None:
    """
    Function called at each TRNSYS iteration within a time step.

    Parameters
    ----------
    TRNData : Dict[str, Dict[str, List[Union[int, float]]]]
        A nested dictionary containing simulation data.

    Returns
    -------
    None
        This function does not return any value.

    """
    
    return

# --------------------------------------------------------------------------------

def EndOfTimeStep(TRNData: Dict[str, Dict[str, List[Union[int, float]]]]) -> None:
    """
    Perform end-of-time-step actions on connected modbus_servers based on TRNData.

    Parameters
    ----------
    TRNData : Dict[str, Dict[str, List[Union[int, float]]]]
        A nested dictionary containing simulation data.

    Returns
    -------
    None
        This function does not return any value.

    Raises
    ------
    Exception
        If an error occurs during the end-of-time-step actions, an exception is raised
        with details about the error.

    Notes
    -----
    This function iterates over connected modbus_servers, writes inputs based on the provided
    TRNData, and reads outputs if applicable. It logs relevant information during the process.

    Examples
    --------
    >>> EndOfTimeStep(TRNData)

    The above example performs end-of-time-step actions on connected modbus_servers using the
    values provided in 'TRNData'.

    """
    
    try:
    
        for modbus_server in modbus_servers:
            TRNinputs = TRNData[SIMULATION_MODEL]["inputs"]
            server_inputs = []

            for index in modbus_server.input_indexes:
                if 0 < index < len(TRNinputs):
                    server_inputs.append(TRNinputs[index])
            modbus_server.write_inputs_modbus(server_inputs)

            if modbus_server.r_registers:
                modbus_server.read_outputs_modbus(TRNData)
        
        logging.info(f"server_inputs: {server_inputs}")

    except Exception as e:
        logging.error(f"Error during EndOfTimeStep: {e}")

    osTime.sleep(SIM_SLEEP)

# --------------------------------------------------------------------------------

def LastCallOfSimulation(TRNData: Dict[str, Dict[str, List[Union[int, float]]]]) -> None:
    """
    Function called at the end of the simulation (once).
    Outputs are meaningless at this call.

    This function closes the Modbus TCP clients connected to PLCs
    and shuts down the logging module.

    Parameters
    ----------
    TRNData : Dict[str, Dict[str, List[Union[int, float]]]]
        A nested dictionary containing simulation data.

    Returns
    -------
    None
        This function does not return any value.

    Raises
    ------
    Exception
        If an error occurs during the last call of the simulation, an exception is raised.
        The error is logged using the logging module.

    Examples
    --------
    >>> trn_data = {'SIMULATION_MODEL': {'outputs': [0, 0, 0]}}
    >>> LastCallOfSimulation(trn_data)
    >>> # Perform actions at the end of the entire TRNSYS simulation

    """

    try:
        for modbus_server in modbus_servers:
            modbus_server.close_connection_modbus()
        
        logging.shutdown()

    except Exception as e:
        logging.error(f"Error during the last call of simulation - modbus: {e}")
        raise

    if xml_server_process:
        xml_server_process.terminate()

    return