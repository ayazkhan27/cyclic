import re

# Function to read the KHAN test log and count success/failure
def analyze_khan_log(log_path):
    with open(log_path, 'r') as file:
        lines = file.readlines()
    
    total_tests = len([line for line in lines if "start_position" in line])
    success_tests = len([line for line in lines if "Passed" in line])
    failure_tests = total_tests - success_tests

    success_rate = (success_tests / total_tests) * 100
    return total_tests, success_tests, failure_tests, success_rate

# Function to read the RSA test vectors and count success/failure
def analyze_rsa_log(log_path):
    with open(log_path, 'r') as file:
        lines = file.readlines()
    
    total_tests = len([line for line in lines if "COUNT =" in line])
    success_tests = len([line for line in lines if "Result = Pass" in line])
    failure_tests = total_tests - success_tests

    success_rate = (success_tests / total_tests) * 100
    return total_tests, success_tests, failure_tests, success_rate

# Paths to the log files
khan_log_path = 'C:/Users/admin/Documents/GitHub/cyclic/test_log.txt'
rsa_log_path = 'C:/Users/admin/Documents/GitHub/cyclic/RSADPComponent800_56B.txt'

# Analyze the logs
khan_total, khan_success, khan_failure, khan_success_rate = analyze_khan_log(khan_log_path)
rsa_total, rsa_success, rsa_failure, rsa_success_rate = analyze_rsa_log(rsa_log_path)

# Display the results
print(f"KHAN Encryption - Total Tests: {khan_total}, Success: {khan_success}, Failure: {khan_failure}, Success Rate: {khan_success_rate:.2f}%")
print(f"RSA - Total Tests: {rsa_total}, Success: {rsa_success}, Failure: {rsa_failure}, Success Rate: {rsa_success_rate:.2f}%")


