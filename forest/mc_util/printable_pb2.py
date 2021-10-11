# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# pylint: skip-file
# type: ignore
# source: printable.proto
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from google.protobuf import reflection as _reflection
from google.protobuf import symbol_database as _symbol_database

# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()


from . import external_pb2 as external__pb2


DESCRIPTOR = _descriptor.FileDescriptor(
    name="printable.proto",
    package="printable",
    syntax="proto3",
    serialized_options=b"\n\022com.mobilecoin.api",
    create_key=_descriptor._internal_create_key,
    serialized_pb=b'\n\x0fprintable.proto\x12\tprintable\x1a\x0e\x65xternal.proto"^\n\x0ePaymentRequest\x12/\n\x0epublic_address\x18\x01 \x01(\x0b\x32\x17.external.PublicAddress\x12\r\n\x05value\x18\x02 \x01(\x04\x12\x0c\n\x04memo\x18\x03 \x01(\t"\x8a\x01\n\x0fTransferPayload\x12\x18\n\x0croot_entropy\x18\x01 \x01(\x0c\x42\x02\x18\x01\x12\x38\n\x11tx_out_public_key\x18\x02 \x01(\x0b\x32\x1d.external.CompressedRistretto\x12\x0c\n\x04memo\x18\x03 \x01(\t\x12\x15\n\rbip39_entropy\x18\x04 \x01(\x0c"\xbe\x01\n\x10PrintableWrapper\x12\x31\n\x0epublic_address\x18\x01 \x01(\x0b\x32\x17.external.PublicAddressH\x00\x12\x34\n\x0fpayment_request\x18\x02 \x01(\x0b\x32\x19.printable.PaymentRequestH\x00\x12\x36\n\x10transfer_payload\x18\x03 \x01(\x0b\x32\x1a.printable.TransferPayloadH\x00\x42\t\n\x07wrapperB\x14\n\x12\x63om.mobilecoin.apib\x06proto3',
    dependencies=[
        external__pb2.DESCRIPTOR,
    ],
)


_PAYMENTREQUEST = _descriptor.Descriptor(
    name="PaymentRequest",
    full_name="printable.PaymentRequest",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="public_address",
            full_name="printable.PaymentRequest.public_address",
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="value",
            full_name="printable.PaymentRequest.value",
            index=1,
            number=2,
            type=4,
            cpp_type=4,
            label=1,
            has_default_value=False,
            default_value=0,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="memo",
            full_name="printable.PaymentRequest.memo",
            index=2,
            number=3,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=46,
    serialized_end=140,
)


_TRANSFERPAYLOAD = _descriptor.Descriptor(
    name="TransferPayload",
    full_name="printable.TransferPayload",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="root_entropy",
            full_name="printable.TransferPayload.root_entropy",
            index=0,
            number=1,
            type=12,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"",
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=b"\030\001",
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="tx_out_public_key",
            full_name="printable.TransferPayload.tx_out_public_key",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="memo",
            full_name="printable.TransferPayload.memo",
            index=2,
            number=3,
            type=9,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"".decode("utf-8"),
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="bip39_entropy",
            full_name="printable.TransferPayload.bip39_entropy",
            index=3,
            number=4,
            type=12,
            cpp_type=9,
            label=1,
            has_default_value=False,
            default_value=b"",
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[],
    serialized_start=143,
    serialized_end=281,
)


_PRINTABLEWRAPPER = _descriptor.Descriptor(
    name="PrintableWrapper",
    full_name="printable.PrintableWrapper",
    filename=None,
    file=DESCRIPTOR,
    containing_type=None,
    create_key=_descriptor._internal_create_key,
    fields=[
        _descriptor.FieldDescriptor(
            name="public_address",
            full_name="printable.PrintableWrapper.public_address",
            index=0,
            number=1,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="payment_request",
            full_name="printable.PrintableWrapper.payment_request",
            index=1,
            number=2,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
        _descriptor.FieldDescriptor(
            name="transfer_payload",
            full_name="printable.PrintableWrapper.transfer_payload",
            index=2,
            number=3,
            type=11,
            cpp_type=10,
            label=1,
            has_default_value=False,
            default_value=None,
            message_type=None,
            enum_type=None,
            containing_type=None,
            is_extension=False,
            extension_scope=None,
            serialized_options=None,
            file=DESCRIPTOR,
            create_key=_descriptor._internal_create_key,
        ),
    ],
    extensions=[],
    nested_types=[],
    enum_types=[],
    serialized_options=None,
    is_extendable=False,
    syntax="proto3",
    extension_ranges=[],
    oneofs=[
        _descriptor.OneofDescriptor(
            name="wrapper",
            full_name="printable.PrintableWrapper.wrapper",
            index=0,
            containing_type=None,
            create_key=_descriptor._internal_create_key,
            fields=[],
        ),
    ],
    serialized_start=284,
    serialized_end=474,
)

_PAYMENTREQUEST.fields_by_name[
    "public_address"
].message_type = external__pb2._PUBLICADDRESS
_TRANSFERPAYLOAD.fields_by_name[
    "tx_out_public_key"
].message_type = external__pb2._COMPRESSEDRISTRETTO
_PRINTABLEWRAPPER.fields_by_name[
    "public_address"
].message_type = external__pb2._PUBLICADDRESS
_PRINTABLEWRAPPER.fields_by_name["payment_request"].message_type = _PAYMENTREQUEST
_PRINTABLEWRAPPER.fields_by_name["transfer_payload"].message_type = _TRANSFERPAYLOAD
_PRINTABLEWRAPPER.oneofs_by_name["wrapper"].fields.append(
    _PRINTABLEWRAPPER.fields_by_name["public_address"]
)
_PRINTABLEWRAPPER.fields_by_name[
    "public_address"
].containing_oneof = _PRINTABLEWRAPPER.oneofs_by_name["wrapper"]
_PRINTABLEWRAPPER.oneofs_by_name["wrapper"].fields.append(
    _PRINTABLEWRAPPER.fields_by_name["payment_request"]
)
_PRINTABLEWRAPPER.fields_by_name[
    "payment_request"
].containing_oneof = _PRINTABLEWRAPPER.oneofs_by_name["wrapper"]
_PRINTABLEWRAPPER.oneofs_by_name["wrapper"].fields.append(
    _PRINTABLEWRAPPER.fields_by_name["transfer_payload"]
)
_PRINTABLEWRAPPER.fields_by_name[
    "transfer_payload"
].containing_oneof = _PRINTABLEWRAPPER.oneofs_by_name["wrapper"]
DESCRIPTOR.message_types_by_name["PaymentRequest"] = _PAYMENTREQUEST
DESCRIPTOR.message_types_by_name["TransferPayload"] = _TRANSFERPAYLOAD
DESCRIPTOR.message_types_by_name["PrintableWrapper"] = _PRINTABLEWRAPPER
_sym_db.RegisterFileDescriptor(DESCRIPTOR)

PaymentRequest = _reflection.GeneratedProtocolMessageType(
    "PaymentRequest",
    (_message.Message,),
    {
        "DESCRIPTOR": _PAYMENTREQUEST,
        "__module__": "printable_pb2"
        # @@protoc_insertion_point(class_scope:printable.PaymentRequest)
    },
)
_sym_db.RegisterMessage(PaymentRequest)

TransferPayload = _reflection.GeneratedProtocolMessageType(
    "TransferPayload",
    (_message.Message,),
    {
        "DESCRIPTOR": _TRANSFERPAYLOAD,
        "__module__": "printable_pb2"
        # @@protoc_insertion_point(class_scope:printable.TransferPayload)
    },
)
_sym_db.RegisterMessage(TransferPayload)

PrintableWrapper = _reflection.GeneratedProtocolMessageType(
    "PrintableWrapper",
    (_message.Message,),
    {
        "DESCRIPTOR": _PRINTABLEWRAPPER,
        "__module__": "printable_pb2"
        # @@protoc_insertion_point(class_scope:printable.PrintableWrapper)
    },
)
_sym_db.RegisterMessage(PrintableWrapper)


DESCRIPTOR._options = None
_TRANSFERPAYLOAD.fields_by_name["root_entropy"]._options = None
# @@protoc_insertion_point(module_scope)
