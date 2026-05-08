/*
 * Copyright (c) 2024 Your Name
 * SPDX-License-Identifier: Apache-2.0
 */

`default_nettype none

module tt_um_lpf_ieee (
    input  wire [7:0] ui_in,    // Dedicated inputs
    output wire [7:0] uo_out,   // Dedicated outputs
    input  wire [7:0] uio_in,   // IOs: Input path
    output wire [7:0] uio_out,  // IOs: Output path
    output wire [7:0] uio_oe,   // IOs: Enable path (active high: 0=input, 1=output)
    input  wire       ena,      // always 1 when the design is powered, so you can ignore it
    input  wire       clk,      // clock
    input  wire       rst_n     // reset_n - low to reset
);

  // All output pins must be assigned. If not used, assign to 0.
    assign uio_out[3:0] =4'b0000;//unused
    assign uio_oe[3:0] = 4'b0000;//act as input uio_in(0-3)
    assign uio_oe[7:4]=4'b1111; // act as output uio_out(4-7)

  // List all unused inputs to prevent warnings
    wire _unused = &{ena, uio_in[7:4], 1'b0};

    wire [11:0] din = {uio_in[3:0],ui_in};
    wire [11:0] dout = {uio_out[7:4],uo_out};

//Instantiate Filter module
    low_area_lpf filter0(
        .clk(clk),
        .rst_n(rst_n),
        .data_in(din),
        .data_out(dout)
    );

endmodule

// Verilog code for Moving average LPF
module low_area_lpf #(
    parameter DATA_WIDTH = 12,
    parameter TAPS = 8 // Must be power of 2 for easy division
)(
    input  wire clk,
    input  wire rst_n,
    input  wire [DATA_WIDTH-1:0] data_in,
    output reg  [DATA_WIDTH-1:0] data_out
);

    reg [DATA_WIDTH-1:0] shift_reg [0:TAPS-1];
    reg [DATA_WIDTH+3:0] sum; // Extra bits to prevent overflow
    reg [3:0] i;

    always @(posedge clk) begin
        if (!rst_n) begin
            sum <= 0;
            data_out <= 0;
            for (i = 0; i < TAPS; i = i + 1) shift_reg[i] <= 0;
        end else begin
            // Update sum: Add new sample, subtract the oldest sample
            sum <= sum + data_in - shift_reg[TAPS-1];

            // Shift data
            for (i = TAPS-1; i > 0; i = i - 1) begin
                shift_reg[i] <= shift_reg[i-1];
            end
            shift_reg[0] <= data_in;

            // Output the average (Arithmetic shift right by 3 for 8 taps)
            data_out <= sum >> 3; 
        end
    end
endmodule
