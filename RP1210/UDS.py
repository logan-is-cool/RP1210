"""A package for parsing and creating Unified Diagnostic Services messages."""

ServiceNames = {
    # Diagnostic and Communications Management
    0x10 : "Diagnostic Session Control",
    0x11 : "ECU Reset",
    0x27 : "Security Access",
    0x28 : "Communication Control",
    0x29 : "Authentication",
    0x3E : "Tester Present",
    0x83 : "Access Timing Parameters",
    0x84 : "Secured Data Transmission",
    0x85 : "Control DTC Settings",
    0x86 : "Response On Event",
    0x87 : "Link Control",
    # Data Transmission
    0x22 : "Read Data By Identifier",
    0x23 : "Read Memory By Address",
    0x24 : "Read Scaling Data By Identifier",
    0x2A : "Read Data By Identifier Periodic",
    0x2C : "Dynamically Define Data Identifier",
    0x2E : "Write Data By Identifier",
    0x3D : "Write Memory By Address",
    # Stored Data Transmission
    0x14 : "Clear Diagnostic Information",
    0x19 : "Read DTC Information",
    # Input / Output Control
    0x2F : "Input Output Control By Identifier",
    # Remote Activation of Routine
    0x31 : "Routine Control",
    # Upload / Download
    0x34 : "Request Download",
    0x35 : "Request Upload",
    0x36 : "Transfer Data",
    0x37 : "Request Transfer Exit",
    0x38 : "Request File Transfer",
    # Negative Response (not a service)
    0x3F : "Negative Response"
}
"""Dict of service names, organized by UDS Request SID."""

ResponseCodes = {
    0x00 : "Positive Response",
    0x10 : "General Reject",
    0x11 : "Service Not Supported",
    0x12 : "Sub-Function Not Supported",
    0x13 : "Incorrect Message Length Or Invalid Format",
    0x14 : "Response Too Long",
    0x21 : "Busy - Repeat Request",
    0x22 : "Conditions Not Correct",
    0x24 : "Request Sequence Error",
    0x25 : "No Response From Subnet Component",
    0x26 : "Failure Prevents Execution Of Requested Action",
    0x31 : "Request Out Of Range",
    0x33 : "Security Access Denied",
    0x34 : "Authentication Required",
    0x35 : "Invalid Key",
    0x36 : "Exceed Number Of Attempts",
    0x37 : "Required Time Delay Not Expired",
    0x38 : "Secure Data Transmission Required",
    0x39 : "Secure Data Transmission Not Allowed",
    0x3A : "Secure Data Verification Failed",
    0x50 : "Certificate verification failed - Invalid Time Period",
    0x51 : "Certificate verification failed - Invalid Signature",
    0x52 : "Certificate verification failed - Invalid Chain of Trust",
    0x53 : "Certificate verification failed - Invalid Type",
    0x54 : "Certificate verification failed - Invalid Format",
    0x55 : "Certificate verification failed - Invalid Content",
    0x56 : "Certificate verification failed - Invalid Scope",
    0x57 : "Certificate verification failed - Invalid Certificate (revoked)",
    0x58 : "Ownership verification failed",
    0x59 : "Challenge calculation failed",
    0x5A : "Setting Access Rights failed",
    0x5B : "Session key creation/derivation failed",
    0x5C : "Configuration data usage failed",
    0x5D : "DeAuthentication failed",
    0x70 : "Upload/Download Not Accepted",
    0x71 : "Transfer Data Suspended",
    0x72 : "General Programming Failure",
    0x73 : "Wrong Block Sequence Counter",
    0x78 : "Request Correctly Received - Response Pending",
    0x7E : "Sub-Function Not Supported In Active Session",
    0x7F : "Service Not Supported In Active Session",
    0x81 : "RPM Too High",
    0x82 : "RPM Too Low",
    0x83 : "Engine Is Running",
    0x84 : "Engine Is Not Running",
    0x85 : "Engine Run Time Too Low",
    0x86 : "Temperature Too High",
    0x87 : "Temperature Too Low",
    0x88 : "Vehicle Speed Too High",
    0x89 : "Vehicle Speed Too Low",
    0x8A : "Throttle/Pedal Too High",
    0x8B : "Throttle/Pedal Too Low",
    0x8C : "Transmission Range Not In Neutral",
    0x8D : "Transmission Range Not In Gear",
    0x8F : "Brake Switch(es) Not Closed (Brake Pedal not pressed or not applied)",
    0x90 : "Shifter Lever Not In Park",
    0x91 : "Torque Converter Clutch Locked",
    0x92 : "Voltage Too High",
    0x93 : "Voltage Too Low",
    0x94 : "Resource Temporarily Not Available",
}
"""Dict of response code definitions. Missing values are reserved by ISO/SAE or proprietary."""

def translateRequestSID(sid : int) -> str:
    """Translates a UDS Request SID (service ID) to its service name."""
    return ServiceNames.get(sid, "Proprietary/Reserved")

def translateResponseSID(sid : int) -> str:
    """Translates a UDS Response SID (service ID) to its service name."""
    return ServiceNames.get(sid - 0x40, "Proprietary/Reserved")

def translateResponseCode(code : int) -> str:
    """Returns a description of the specified UDS response code."""
    # cover some specific cases
    if 0x95 <= code <= 0xEF:
        return "Reserved For Specific Conditions Not Correct"
    if 0xF0 <= code <= 0xFE:
        return "Conditions Not Correct: Vehicle Manufacturer Specific"
    return ResponseCodes.get(code, "ISO/SAE Reserved")
