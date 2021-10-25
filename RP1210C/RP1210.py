"""
While I try to provide adequate documentation, the RP1210C standard is owned by TMC, not me, and is
not reproduced here. For a complete understanding of the RP1210 standard, you must purchase and
read the RP1210C documentation from TMC.

RP1210C documentation can be purchased from TMC at this link ($37.50 at time of writing):
    https://www.atabusinesssolutions.com/Shopping/Product/viewproduct/2675472/TMC-Individual-RP
"""
import os
import configparser
from configparser import ConfigParser
from ctypes import POINTER, c_char_p, c_int32, c_long, c_short, c_void_p, cdll, CDLL, create_string_buffer

RP1210_ERRORS = {
    1: "NO_ERRORS",
    128: "ERR_DLL_NOT_INITIALIZED",
    129: "ERR_INVALID_CLIENT_ID",
    130: "ERR_CLIENT_ALREADY_CONNECTED",
    131: "ERR_CLIENT_AREA_FULL",
    132: "ERR_FREE_MEMORY",
    133: "ERR_NOT_ENOUGH_MEMORY",
    134: "ERR_INVALID_DEVICE",
    135: "ERR_DEVICE_IN_USE",
    136: "ERR_INVALID_PROTOCOL",
    137: "ERR_TX_QUEUE_FULL",
    138: "ERR_TX_QUEUE_CORRUPT",
    139: "ERR_RX_QUEUE_FULL",
    140: "ERR_RX_QUEUE_CORRUPT",
    141: "ERR_MESSAGE_TOO_LONG",
    142: "ERR_HARDWARE_NOT_RESPONDING",
    143: "ERR_COMMAND_NOT_SUPPORTED",
    144: "ERR_INVALID_COMMAND",
    145: "ERR_TXMESSAGE_STATUS",
    146: "ERR_ADDRESS_CLAIM_FAILED",
    147: "ERR_CANNOT_SET_PRIORITY",
    148: "ERR_CLIENT_DISCONNECTED",
    149: "ERR_CONNECT_NOT_ALLOWED",
    150: "ERR_CHANGE_MODE_FAILED",
    151: "ERR_BUS_OFF",
    152: "ERR_COULD_NOT_TX_ADDRESS_CLAIMED",
    153: "ERR_ADDRESS_LOST",
    154: "ERR_CODE_NOT_FOUND",
    155: "ERR_BLOCK_NOT_ALLOWED",
    156: "ERR_MULTIPLE_CLIENTS_CONNECTED",
    157: "ERR_ADDRESS_NEVER_CLAIMED",
    158: "ERR_WINDOW_HANDLE_REQUIRED",
    159: "ERR_MESSAGE_NOT_SENT",
    160: "ERR_MAX_NOTIFY_EXCEEDED",
    161: "ERR_MAX_FILTERS_EXCEEDED",
    162: "ERR_HARDWARE_STATUS_CHANGE",
    202: "ERR_INI_FILE_NOT_IN_WIN_DIR",
    204: "ERR_INI_SECTION_NOT_FOUND",
    205: "ERR_INI_KEY_NOT_FOUND",
    206: "ERR_INVALID_KEY_STRING",
    207: "ERR_DEVICE_NOT_SUPPORTED",
    208: "ERR_INVALID_PORT_PARAM",
    213: "ERR_COMMAND_TIMED_OUT",
    220: "ERR_OS_NOT_SUPPORTED",
    222: "ERR_COMMAND_QUEUE_IS_FULL",
    224: "ERR_CANNOT_SET_CAN_BAUDRATE",
    225: "ERR_CANNOT_CLAIM_BROADCAST_ADDRESS",
    226: "ERR_OUT_OF_ADDRESS_RESOURCES",
    227: "ERR_ADDRESS_RELEASE_FAILED",
    230: "ERR_COMM_DEVICE_IN_USE",
    441: "ERR_DATA_LINK_CONFLICT",
    453: "ERR_ADAPTER_NOT_RESPONDING",
    454: "ERR_CAN_BAUD_SET_NONSTANDARD",
    455: "ERR_MULTIPLE_CONNECTIONS_NOT_ALLOWED_NOW",
    456: "ERR_J1708_BAUD_SET_NONSTANDARD",
    457: "ERR_J1939_BAUD_SET_NONSTANDARD",
    458: "ERR_IS015765_BAUD_SET_NONSTANDARD",
    600: "ERR_INVALID_IOCTL_ID",
    601: "ERR_NULL_PARAMETER",
    602: "ERR_HARDWARE_NOT_SUPPORTED"}
"""RP1210 error codes. Use this to translate ClientConnect output."""

RP1210_COMMANDS = {
    0 : "Reset_Device",
    3 : "Set_All_Filters_States_to_Pass",
    4 : "Set_Message_Filtering_For_J1939",
    5 : "Set_Message_Filtering_For_CAN",
    7 : "Set_Message_Filtering_For_J1708",
    8 : "Set_Message_Filtering_For_J1850",
    9 : "Set_Message_Filtering_For_ISO15765",
    14 : "Generic_Driver_Command",
    15 : "Set_J1708_Mode",
    16 : "Echo_Transmitted_Messages",
    17 : "Set_All_Filters_States_to_Discard",
    18 : "Set_Message_Receive",
    19 : "Protect_J1939_Address",
    20 : "Set_Broadcast_For_J1708",
    21 : "Set_Broadcast_For_CAN",
    22 : "Set_Broadcast_For_J1939",
    23 : "Set_Broadcast_For_J1850",
    24 : "Set_J1708_Filter_Type",
    25 : "Set_J1939_Filter_Type",
    26 : "Set_CAN_Filter_Type",
    27 : "Set_J1939_Interpacket_Time",
    28 : "SetMaxErrorMsgSize",
    29 : "Disallow_Further_Connections",
    30 : "Set_J1850_Filter_Type",
    31 : "Release_J1939_Address",
    32 : "Set_ISO15765_Filter_Type",
    33 : "Set_Broadcast_For_ISO15765",
    34 : "Set_ISO15765_Flow_Control",
    35 : "Clear_ISO15765_Flow_Control",
    37 : "Set_J1939_Baud",
    38 : "Set_ISO15765_Baud",
    215 : "Set_BlockTimeout",
    305 : "Set_J1708_Baud",
    39 : "Flush_Tx_Rx_Buffers",
    41 : "Set_Broadcast_For_KWP2000",
    42 : "Set_Broadcast_For_ISO9141",
    45 : "Get_Protocol_Connection_Speed",
    46 : "Set_ISO9141KWP2000_Mode",
    47 : "Set_CAN_Baud",
    48 : "Get_Wireless_State"}
"""Mnemonics for RP1210_SendCommand commands. Follows ordering of table in section 21.4."""

IOCTL_IDS = {
    0x01 : "GET_CONFIG",
    0x02 : "SET_CONFIG",
    0x04 : "FIVE_BAUD_INIT",
    0x05 : "FAST_INIT",
    0x06 : "ISO9141_K_LINE_ONLY"
    #0x03, 0x07 - 0xFFFF    reserved for TMC
    #0x10000 - OxFFFFFFFF   vendor specific
}
"""IOCTL ID values - use these to lookup inputs to Ioctl function."""

def translateErrorCode(ClientID :int) -> str:
        """
        Matches clientID with error string in RP1210_ERRORS.

        NO_ERRORS has been expanded to cover clientID = 0 to 127.
        
        If there is no match, returns the clientID as str.
        """
        if 0 <= ClientID < 128:
            return "NO_ERRORS"
        return RP1210_ERRORS.get(ClientID, str(ClientID))

def getAPINames(rp121032_path = None) -> list[str]:
    """
    A function for reading API names from RP121032.ini. Returns a list of strings.

    Just call getAPINames() to get the API names. Then you can initialize
    an RP1210Interface object using one of the API names.

    You can provide your own path to RP121032.ini, or let it find it on its own.

    Returns empty list [] if RP121032.ini isn't found or couldn't be parsed.
    """
    if not rp121032_path: # find our own path if none is given
        rp121032_path = os.path.join(os.environ["WINDIR"], "RP121032.ini")
    if not os.path.isfile(rp121032_path): # check if file exists
        return []
    try:    # read from file
        parser = ConfigParser()
        parser.read(rp121032_path)
        return parser["RP1210Support"]["APIImplementations"].split(",")
    except Exception:
        return []
    
class RP1210Interface(ConfigParser):
    """
    Reads & stores API information. Child of ConfigParser. Use RP121032Parser to get an
    RP1210 API name to feed to this class.

    This class has functions for reading EVERY SINGLE data field defined in the RP1210C standard.
    As such, it is embarrassingly long.

    This class holds an instance of RP1210API, which you can use to call RP1210 functions.
    The interface is accessed via the function api(), e.g.:
        nexiq = RP1210Interface("NULN2R32")
         clientID = nexiq.api().ClientConnect(args)

    You can use str(this_object) to generate a string to display in your Vendors dropdown.
    """
    def __init__(self, api_name : str) -> None:
        super().__init__()
        self.api_name = api_name
        self.api_valid = True
        self.devices = []   # type: list[RP1210Device]
        self.API = RP1210API(api_name)

        self.populate()

    def __str__(self) -> str:
        """
        Returns a string that you'd typically put in a vendor selection box.
        
        Format: "api_name - adapter_description"

        Appends " - (drivers invalid)" if drivers failed to load.
        """
        if self.api_valid:
            err_str = ""
        else:
            err_str = " - (drivers invalid)"
        return self.getAPIName() + " - " + self.getName() + err_str

    def api(self):
        """
        Returns RP1210API object that can be used to call RP1210 functions.
        
        If DLL has not yet been loaded, will load DLL before returning API.
        """
        return self.API

    def isValid(self) -> bool:
        """
        Returns self.api_valid, which is set to False if drivers fail to load,
        devices can't be read, etc.

        This function DOES NOT run through any checks before returning api_valid - so don't
        call it right away!
            e.g. you can't call isValid() to see if you can call getDLL() - call getDLL() first.
        """
        return self.api_valid

    def getAPIName(self) -> str:
        """Returns API name (i.e. the name of the .ini and .dll files)"""
        return self.api_name

    def getName(self) -> str:
        """
        Returns 'Name' field from VendorInformation section.

        Will return "(Vendor Name Missing)" if the 'Name' field isn't found.
        """
        if not self.has_option("VendorInformation", "Name"):
            return "(Vendor Name Missing)"
        return self.get("VendorInformation", "Name")

    def getAddress1(self) -> str:
        """
        Returns 'Address1' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Address1"):
            return ""
        return self.get("VendorInformation", "Address1")

    def getAddress2(self) -> str:
        """
        Returns 'Address2' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Address2"):
            return ""
        return self.get("VendorInformation", "Address2")

    def getCity(self) -> str:
        """
        Returns 'Address2' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "City"):
            return ""
        return self.get("VendorInformation", "City")

    def getState(self) -> str:
        """
        Returns 'State' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "State"):
            return ""
        return self.get("VendorInformation", "State")

    def getCountry(self) -> str:
        """
        Returns 'Country' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Country"):
            return ""
        return self.get("VendorInformation", "Country")

    def getPostal(self) -> str:
        """
        Returns 'Postal' field (zipcode) from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Postal"):
            return ""
        return self.get("VendorInformation", "Postal")

    def getTelephone(self) -> str:
        """
        Returns 'Telephone' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Telephone"):
            return ""
        return self.get("VendorInformation", "Telephone")

    def getFax(self) -> str:
        """
        Returns 'Fax' field from VendorInformation section.

        Returns an empty string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "Fax"):
            return ""
        return self.get("VendorInformation", "Fax")

    def getVendorURL(self) -> str:
        """
        Returns the VendorURL field in VendorInformation section.
        
        Returns empty string if VendorURL field isn't found.
        """
        if not self.has_option("VendorInformation", "VendorURL"):
            return ""
        return self.get("VendorInformation", "VendorURL")

    def getVersion(self) -> int:
        """
        Returns the 'Version' field in VendorInformation section.
        
        Returns None if Version field isn't found.
        """
        if not self.has_option("VendorInformation", "Version"):
            return None
        try:
            return self.getint("VendorInformation", "Version")
        except (ValueError, KeyError):
            return None

    def autoDetectCapable(self) -> bool:
        """
        Returns the 'AutoDetectCapable' field in VendorInformation section.

        Returns False if the field isn't found.
        """
        if not self.has_option("VendorInformation", "AutoDetectCapable"):
            return False
        try:
            return self.getboolean("VendorInformation", "AutoDetectCapable")
        except (ValueError, KeyError):
            return False

    def getTimeStampWeight(self) -> float:
        """
        Returns the 'TimeStampWeight' field in VendorInformation section.

        Returns None if the field isn't found.
        """
        if not self.has_option("VendorInformation", "TimeStampWeight"):
            return None
        try:
            return self.getfloat("VendorInformation", "TimeStampWeight")
        except (ValueError, KeyError):
            return None

    def getMessageString(self) -> str:
        """
        Returns the 'MessageString' field in VendorInformation section.

        Returns a blank string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "MessageString"):
            return ""
        return self.get("VendorInformation", "MessageString")

    def getErrorString(self) -> str:
        """
        Returns the 'ErrorString' field in VendorInformation section.

        Returns a blank string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "ErrorString"):
            return ""
        return self.get("VendorInformation", "ErrorString")

    def getRP1210Version(self) -> str:
        """
        Returns the 'RP1210' field in VendorInformation section.

        Returns a blank string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "RP1210Version"):
            return ""
        return self.get("VendorInformation", "RP1210Version")

    def getDebugLevel(self) -> int:
        """
        Returns the 'DebugLevel' field in VendorInformation section.
        - -1 = Debugging is not supported by this API.
        - 0 = No debugging to be accomplished.
        - 1 = Only Connect/Disconnect/Error Messages.
        - 2 = Add RP1210 SendCommand calls.
        - 3 = Add all sent Messages (with filtering).
        - 4 = Add all Received Messages (with filtering).

        Returns -1 (debugging not supported) if the field isn't found.
        """
        if not self.has_option("VendorInformation", "DebugLevel"):
            return -1
        try:
            return self.getint("VendorInformation", "DebugLevel")
        except (ValueError, KeyError):
            return -1

    def getDebugFile(self) -> str:
        """
        Returns the 'DebugFile' field in VendorInformation section.

        This represents the absolute path to the debug/log file.

        Returns a blank string if the field isn't found.
        """
        if not self.has_option("VendorInformation", "DebugFile"):
            return ""
        return self.get("VendorInformation", "DebugFile")

    def getDebugMode(self) -> int:
        """
        Returns the 'DebugMode' field in VendorInformation section.
        - 0 = Overwrite (completely destroying previous contents) 
        - 1 = Append (write to the end of the file, keeping any previous contents) 

        Returns None if the field isn't found.
        """
        if not self.has_option("VendorInformation", "DebugMode"):
            return None
        try:
            return self.getint("VendorInformation", "DebugMode")
        except (ValueError, KeyError):
            return None

    def getDebugFileSize(self) -> int:
        """
        Returns the 'DebugFileSize' field in VendorInformation section.
        
        This represents the maximum size in kilobytes that the debug file should be.
        If this field is missing (and debug logging is enabled), it defaults to 1024 KB (1MB).

        Returns 1024 (default size) if the field isn't found. Please note that if DebugLevel = -1,
        there will be no logging even if you receive a value of 1024 from this function.
        """
        if not self.has_option("VendorInformation", "DebugFileSize"):
            return 1024
        try:
            return self.getint("VendorInformation", "DebugFileSize")
        except (ValueError, KeyError):
            return 1024

    def getNumberOfSessions(self) -> int:
        """
        Returns the 'NumberOfRTSCTSSessions' field in VendorInformation section.

        'NumberOfRTSCTSSessions' is an integer representing the number of concurrent RTS/CTS
        transport sessions that the API supports per client.

        Returns 1 (default value) if the field isn't found.
        """
        if not self.has_option("VendorInformation", "NumberOfSessions"):
            return 1
        try:
            return self.getint("VendorInformation", "NumberOfSessions")
        except (ValueError, KeyError):
            return 1

    def getCANFormatsSupported(self) -> list[int]:
        """
        Returns the 'CANFormatsSupported' list in VendorInformation section.

        These numbers correspond with the CAN Formats described in section 12.8 of the RP1210C 
        documentation.

        Returns an empty list if the field isn't found.
        """
        if not self.has_option("VendorInformation", "CANFormatsSupported"):
            return []
        try:
            return self["VendorInformation"]["CANFormatsSupported"].split(",")
        except Exception:
            return []

    def getJ1939FormatsSupported(self) -> list[int]:
        """
        Returns the 'J1939FormatsSupported' list in VendorInformation section.

        These numbers correspond with the CAN Formats described in section 12.8 of the RP1210C 
        documentation.

        Returns an empty list if the field isn't found.
        """
        if not self.has_option("VendorInformation", "J1939FormatsSupported"):
            return []
        try:
            return self["VendorInformation"]["J1939FormatsSupported"].split(",")
        except Exception:
            return []

    def populate(self):
        """Reads .ini file for the specified RP1210 API."""
        try:
            self.read(self.getPath())
        except configparser.Error:
            self.api_valid = False

    def getPath(self):
        """Returns absolute path to API config file."""
        return os.path.join(os.environ["WINDIR"], self.api_name + ".ini")

class RP1210API:
    """
    Interface with RP1210 API to call functions from your adapter's drivers.

    See function docstrings for details on each function.
    """
    def __init__(self, api_name : str) -> None:
        self.api_valid = False
        self.api_name = api_name

    def getDLL(self) -> CDLL:
        """
        Returns CDLL object for this RP1210 API.

        Will return None if cdll.LoadLibrary was unsuccessful.
        """
        if not self.dll:
            self.loadDLL()
        return self.dll

    def loadDLL(self) -> CDLL:
        """
        Loads and returns CDLL for this API.
        
        If you already called loadDLL(), you can call getDLL() to get the DLL you loaded previously.
        """
        try:
            try:
                path = self.api_name + ".dll"
                dll = cdll.LoadLibrary(path)
            except WindowsError:
                # Try "DLL installed in wrong directory" band-aid
                path = self.__get_dll_path_aux()
                dll = cdll.LoadLibrary(path)
            self.setDLL(dll)
            return dll
        except Exception: # RIP
            self.api_valid = False
            return None

    def isValid(self) -> bool:
        """
        Returns api_valid boolean, which is set when the DLL is loaded.
        
        True = DLL loaded, False = DLL failed to load
        """
        return self.api_valid

    def setDLL(self, dll : CDLL):
        """Sets the CDLL used to call RP1210 API functions."""
        try:
            self.dll = dll
            if self.dll: # check it's not None
                self.__init_functions()
                self.api_valid = True
            else:
                self.api_valid = False
        except OSError:
            self.api_valid = False

    def ClientConnect(self, DeviceID : int, Protocol : str, TxBufferSize = 0, 
                            RcvBufferSize = 0, isAppPacketizingincomingMsgs = 0) -> int:
        """
        Attempts to connect to an RP1210 adapter.
        - nDeviceID determines which adapter it tries to connect to.
        - You can generate fpchProtocol with a ProtocolFormatter class, e.g. J1939ProtocolFormatter,
        use RP1210Protocol class to read supported formats from file, or just do it yourself.
        - Tx and Rcv buffer sizes default to 8K when given an argument of 0.
        - Don't mess with argument nisAppPacketizingincomingMsgs.

        Returns nDeviceID. 0 to 127 means connection was successful; >127 means it failed.

        Use function translateClientID() to translate nClientID to an error message.
        """
        return self.getDLL().RP1210_ClientConnect(0, DeviceID, Protocol, TxBufferSize, 
                                                RcvBufferSize, isAppPacketizingincomingMsgs)
    
    def ClientDisconnect(self, ClientID : int) -> int:
        """
        Disconnects from client w/ specified clientID.
        
        Returns 0 if successful, or >127 if it failed.
            You can use translateClientID() to translate the failure code.
        """
        return self.getDLL().RP1210_ClientDisconnect(ClientID)

    def SendMessage(self, ClientID : int, ClientMessage : str, MessageSize : int) -> int:
        """
        Send a message to the databus your adapter is connected to.
        - nClientID = clientID you got from ClientConnect
        - fpchClientMessage = message you want to send
        - nMessageSize = message size in bytes (including identifier, checksum, etc)
        
        Use a Message class provided with this package (e.g. J1939Message) to generate arguments
        fpchClientMessage and nMessageSize.

        Returns 0 if successful, or >127 if it failed.
            You can use translateClientID() to translate the failure code.
        """
        return self.getDLL().RP1210_SendMessage(ClientID, ClientMessage, MessageSize, 0, 0)

    def ReadMessage(self, ClientID : int, RxBuffer : bytearray, BufferSize : int, 
                        BlockOnRead = 0) -> int:
        """
        Rx function.
        - ClientID = clientID you got from ClientConnect
        - RxBuffer = buffer you want to read the message into (called fpchAPIMessage in RP1210 docs)
        - BufferSize = the size of the buffer in bytes.
        - BlockOnRead = sets NON_BLOCKING_IO or BLOCKING_IO. Defaults to NON_BLOCKING_IO.
        
        Returns the number of bytes read (including 4 bytes for timestamp). Returns 0 if no message
        is present.
        """
        return self.getDLL().RP1210_ReadMessage(ClientID, RxBuffer, BufferSize, BlockOnRead)

    def ReadDirect(self, ClientID : int, BufferSize = 512, BlockOnRead = 0) -> bytearray:
        """
        Calls ReadMessage, but generates and returns its own RxBuffer as a bytearray.
        - ClientID = clientID you got from ClientConnect
        - BufferSize = the size of the buffer in bytes. Defaults to 512.
        - BlockOnRead = sets NON_BLOCKING_IO or BLOCKING_IO. Defaults to NON_BLOCKING_IO.

        Automatically cuts array size to the message size reported by ReadMessage().

        Output still includes leading 4 timestamp bytes.
        """
        RxBuffer = bytearray(BufferSize)
        size = self.getDLL().RP1210_ReadMessage(ClientID, RxBuffer, BufferSize, BlockOnRead)
        return RxBuffer[:size]

    def ReadVersionDirect(self, BufferSize = 16) -> tuple:
        """
        Reads API and DLL version info. Returns a tuple containing (in order):
        - DLLMajorVersion (str)
        - DLLMinorVersion (str)
        - APIMajorVersion (str)
        - APIMinorVersion (str)

        Arg BufferSize can be used to specify the size of the buffers used to read each element.

        This function checks your RP1210 drivers; there is no communication with an adapter.
        """
        DLLMajorVersion = create_string_buffer(BufferSize)
        DLLMinorVersion = create_string_buffer(BufferSize)
        APIMajorVersion = create_string_buffer(BufferSize)
        APIMinorVersion = create_string_buffer(BufferSize)
        self.getDLL().RP1210_ReadVersion(DLLMajorVersion, DLLMinorVersion, 
                                        APIMajorVersion, APIMinorVersion)
        return (DLLMajorVersion.value, DLLMinorVersion.value,
                APIMajorVersion.value, APIMinorVersion.value)
        
    def ReadDetailedVersionDirect(self, ClientID : int) -> tuple:
        """
        Reads API, DLL, and adapter firmware version info. Returns a tuple containing (in order):
        - APIVersionInfo (str)
        - DLLVersionInfo (str)
        - FWVersionInfo (str) (this is from the adapter)

        This function communicates with your adapter to read firmware info.
        """
        APIVersionInfo = create_string_buffer(17)
        DLLVersionInfo = create_string_buffer(17)
        FWVersionInfo = create_string_buffer(17)
        self.getDLL().RP1210_ReadDetailedVersion(ClientID, APIVersionInfo, DLLVersionInfo, FWVersionInfo)
        return (APIVersionInfo.value, DLLVersionInfo.value, FWVersionInfo.value)

    def GetErrorMsgDirect(self, ErrorCode : int) -> str:
        """
        Returns 'a textual representation of the last error code that occurred by that client in an
        application.'
        - ErrorCode = 'Numerical value for the last error which occurred.'

        If GetErrorMsg fails, this function will return the GetErrorMsg code (generally ERR_CODE_NOT_FOUND).
        """
        ErrorMsg = create_string_buffer(80)
        ret_code = self.getDLL().RP1210_GetErrorMsg(ErrorCode, ErrorMsg)
        if ret_code == 0:
            return ErrorMsg.value
        else:
            return translateErrorCode(ret_code)

    def GetHardwareStatusDirect(self, ClientID : int, InfoSize = 64) -> bytearray:
        """
        Calls GetHardwareStatus and returns the result directly.

        InfoSize must be 16 <= InfoSize <= 64, and must be a multiple of 2.
        """
        ClientInfo = bytearray(InfoSize)
        self.getDLL().RP1210_GetHardwareStatus(ClientID, ClientInfo, InfoSize, 0)
        return ClientInfo

    def SendCommand(self, CommandNumber : int, ClientID : int, ClientCommand = "", MessageSize = 0) -> int:
        """
        Calls RP1210_SendCommand.
        """
        return self.getDLL().RP1210_SendCommand(CommandNumber, ClientID, ClientCommand, MessageSize)

    def __init_functions(self):
        """Give Python type hints for interfacing with the DLL."""
        self.dll.RP1210_ClientConnect.argtypes = [c_long, c_short, c_char_p, c_long, c_long, c_short]
        self.dll.RP1210_ClientDisconnect.argtypes = [c_short]
        self.dll.RP1210_SendMessage.argtypes = [c_short, c_char_p, c_short, c_short, c_short]
        self.dll.RP1210_ReadMessage.argtypes = [c_short, c_char_p, c_short, c_short]
        self.dll.RP1210_ReadVersion.argtypes = [c_char_p, c_char_p, c_char_p, c_char_p]
        self.dll.RP1210_ReadDetailedVersion.argtypes = [c_short, c_char_p, c_char_p, c_char_p]
        self.dll.RP1210_GetErrorMsg.argtypes = [c_short, c_char_p]
        self.dll.RP1210_GetLastErrorMsg.argtypes = [c_short, POINTER(c_int32), c_char_p, c_short]
        self.dll.RP1210_GetHardwareStatus.argtypes = [c_short, c_char_p, c_short, c_short]
        self.dll.RP1210_SendCommand.argtypes = [c_short, c_short, c_char_p, c_short]
        self.dll.RP1210_Ioctl.argtypes = [c_short, c_long, c_void_p, c_void_p]

    def __get_dll_path_aux(self) -> str:
        """
        Some adapter vendors (looking at you, Actia) install their drivers in the wrong directory.
        This function returns the dll path in that directory.
        """
        return os.path.join(os.environ["WINDIR"], self.api_name + ".dll")

class RP1210Protocol:
    """
    Stores information for an RP1210 protocol, e.g. info stored in ProtocolInformationXXX sections.

    Access information directly, e.g. curr_description = protocols[0].Description

    All values default to empty strings, empty lists, or None if not provided.
    - Description (str)
    - ProtocolSpeed (list[str]) - stored as strings because it can contain "Auto"
    - ProtocolString (str)
    - ProtocolParams (list[str])
    - Devices (list[str])
    """
    def __init__(self,  Description     = "",
                        ProtocolSpeed   = [],
                        ProtocolString  = "",
                        ProtocolParams  = [],
                        Devices         = []) -> None:
        self.Description    = Description
        self.ProtocolSpeed  = ProtocolSpeed
        self.ProtocolString = ProtocolString
        self.ProtocolParams = ProtocolParams
        self.Devices        = Devices

class RP1210Device:
    """
    Stores information for an RP1210 device, e.g. info stored in DeviceInformationXXX sections.

    Use str() to get a pre-made string to put in Device dropdown menu.

    Access information directly, e.g. curr_description = devices[0].Description
    - DeviceID (int)
    - Description (str)
    - DeviceName (str)
    - DeviceParams (str)
    """
    def __init__(self,  DeviceID    = None,
                        Description = "",
                        DeviceName  = "",
                        DeviceParams = "") -> None:
        self.DeviceID       = DeviceID
        self.Description    = Description
        self.DeviceName     = DeviceName
        self.DeviceParams   = DeviceParams