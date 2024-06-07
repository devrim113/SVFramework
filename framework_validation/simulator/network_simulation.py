import subprocess


def __print_success(message):
    print(f"\033[32m{message}\033[0m")


def __print_failure(message):
    print(f"\033[31m{message}\033[0m")


def __print_test(message):
    width = 60
    dot_count = width - len(message)
    print(f"{message}{'.' * max(dot_count, 1)}", end="", flush=True)


def check_qdisc():
    __print_test("Checking if qdisc is set in the loopback interface")
    output = subprocess.run(
        ["tc", "qdisc", "show", "dev", "lo"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    output = output.stdout.decode("utf-8")

    # Check if the qdisc is set
    if "noqueue" in output:
        __print_failure("Failed! No qdisc set in the loopback interface.")
        return False
    __print_success("Success! Qdisc set in the loopback interface.")
    return True


if __name__ == "__main__":
    error_count = 0
    failed_tests = []
    if not check_qdisc():
        error_count += 1
        failed_tests.append("check_qdisc")

    if error_count > 0:
        __print_failure(
            f"Failed! {error_count} tests failed: {', '.join(failed_tests)}"
        )
