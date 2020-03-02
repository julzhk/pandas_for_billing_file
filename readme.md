The instructions are duplicated in the README.md file in the starting code ZIP file that should download.

In this challenge, we’d like you to write a small program which, given a set of meter readings, 
computes a member’s monthly energy bill. To do this, we have stubbed out the following files for you:

bill_member.py, which contains functions to compute the customer bill and print it to screen.
    You should implement calculate_bill. This is the entry point to your solution.
    calculate_bill is currently hardcoded to give the correct answer for August 2017.

There’s no need to change calculate_and_print_bill.
test_bill_member.py, a test module for bill_member.
main.py, the entry point for the program, there’s no need to make changes to this module.
tariff.py, prices by kWh for all energy
load_readings.py, provides a function for loading the readings from the given json.
readings.json, contains a set of monthly meter readings for a given year, member and fuel
We’d like you to:

Implement the calculate_bill function, so that given:
 a member_id, 
 optional account argument 
 and billing date, 
we can compute the bill for the customer.
