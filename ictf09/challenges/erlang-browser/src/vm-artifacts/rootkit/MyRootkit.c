// BASIC DEVICE DRIVER for Challenge 2 / InetSec 2
// Use this template to develop your rootkit code
// Courtesy of SecLab ; TU Wien

#include "ntddk.h"

VOID OnUnload( IN PDRIVER_OBJECT DriverObject )
{
	DbgPrint("OnUnload called\n");
}

NTSTATUS DriverEntry( IN PDRIVER_OBJECT theDriverObject, IN PUNICODE_STRING theRegistryPath )
{
	DbgPrint("I loaded!");

	theDriverObject->DriverUnload  = OnUnload; 

	return STATUS_SUCCESS;
}

