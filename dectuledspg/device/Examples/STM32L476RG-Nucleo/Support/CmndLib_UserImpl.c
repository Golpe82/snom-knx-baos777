/* SPDX-License-Identifier: MIT */

///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
///
/// @file       CmndLib_UserImpl.c
/// @brief      This example shows how to implement functions that were declared in CmndLib_UserImpl.h
///
/// @details
///			CmndLib_UserImpl_xxxx.h files are used to define OS related functions.
///			This source file is an example, how to write an implementation for OS related functions.
///
///
///////////////////////////////////////////////////////////////////////////////////////////////////////////////////////

#include "TypeDefs.h"
#include "stm32l4xx_hal.h"

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

/// function to get current time in milliseconds
u64 p_CmndLib_UserImpl_GetTickCountMs( void )
{
	return (u64)HAL_GetTick();
}

///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////