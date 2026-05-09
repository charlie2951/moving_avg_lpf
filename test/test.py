# SPDX-FileCopyrightText: © 2024 Tiny Tapeout
# SPDX-License-Identifier: Apache-2.0

import cocotb
from cocotb.clock import Clock
from cocotb.triggers import ClockCycles, Timer, RisingEdge
import math
import random


@cocotb.test()
async def test_project(dut):
    dut._log.info("Start")
    # --- Configuration ---
    CLK_PERIOD_NS = 20  # 50 MHz
    FS = 50_000_000     # Sample rate
    F_SIG = 1_000       # Signal frequency 1kHz
    SAMPLES = 30000
    DW_MAX = (2**12) - 1 # 4095
    # Set the clock period to 10 us (100 KHz)
    clock = Clock(dut.clk, CLK_PERIOD_NS, unit="ns")
    cocotb.start_soon(clock.start())

    # Reset
    dut._log.info("Reset")
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0
    await ClockCycles(dut.clk, 10)
    dut.rst_n.value = 1
    dut._log.info("Test project behavior")
    dut._log.info("Applying Noisy Sine Wave...")

    # --- Stimulus Loop ---
    for i in range(SAMPLES):
        # 1. Generate Clean Sine (Mid-range 2048 +/- 1000)
        step = (2 * math.pi * F_SIG * i) / FS
        sine_val = 2048 + (1000 * math.sin(step))

        # 2. Generate Random Noise (Gaussian/Normal distribution)
        noise_val = random.normalvariate(0, 100)

        # 3. Combine and Clip to 12-bit range
        combined_val = int(sine_val + noise_val)
        
        # Manual clipping for safety
        if combined_val > DW_MAX:
            combined_val = DW_MAX
        elif combined_val < 0:
            combined_val = 0
        # Drive the input
        dut.ui_in.value = combined_val & 0xFF
        dut.uio_in.value = (combined_val >> 8) & 0xF
        # Wait for the next clock cycle
        await RisingEdge(dut.clk)
        # Accessing the .value attribute is key
        in_val = int(((dut.uio_in.value.integer & 0xF) << 8) | (dut.ui_in.value.integer & 0xFF))
        out_val = int((((dut.uio_out.value.integer >> 4) & 0xF) << 8) | (dut.uo_out.value.integer & 0xFF))
        # Method B: Recommended Logging (includes simulation time)
        dut._log.info(f"In: {in_val:4d} | Out: {out_val:4d}")
        
    # Set the input values you want to test
    #dut.ui_in.value = 20
    #dut.uio_in.value = 12

    # Wait for one clock cycle to see the output values
    #await ClockCycles(dut.clk, 10)

    # The following assersion is just an example of how to check the output values.
    # Change it to match the actual expected output of your module:
    #assert dut.uo_out.value != 0

    # Keep testing the module by changing the input values, waiting for
    # one or more clock cycles, and asserting the expected output values.
