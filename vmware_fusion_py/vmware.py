# pylint: disable=R0913
# pylint: disable=R0904
"""This module contains the VMware wrapper class and helper functions."""
import subprocess


def _provide_vm_path(func):
    def wrapper(self, *args, **kwargs):
        if "vm_path" in kwargs:
            return func(self, *args, **kwargs)

        if self.vm_path is not None:
            return func(self, vm_path=self.vm_path, *args, **kwargs)

        return func(self, *args, **kwargs)

    return wrapper


class VMware:
    """Wrapper class for the vmrun cli"""

    def __init__(
        self,
        vmrun_path: str,
        host_type: str = "",
        vm_password: str = "",
        guest_user: str = "",
        guest_password: str = "",
        vm_path: str = "",
    ) -> None:

        self.vmrun_path = vmrun_path
        self.host_type = host_type
        self.vm_password = vm_password
        self.guest_user = guest_user
        self.guest_password = guest_password
        self.vm_path = vm_path

    def set_vmrun_path(self, vmrun_path):
        """
        Set the path to the vmrun executable
        :param vmrun_path: Path to the vmrun executable
        """
        self.vmrun_path = vmrun_path

    def set_host_type(self, host_type):
        """
        Set the host type (ws | fusion)
        :param host_type: The type of the host
        """
        self.host_type = host_type

    def set_vm_password(self, vm_password):
        """
        Set the password for the vm
        :param vm_password: The password for the vm
        """
        self.vm_password = vm_password

    def set_guest_user(self, guest_user):
        """
        Set the guest user
        :param guest_user: The guest user
        """
        self.guest_user = guest_user

    def set_guest_password(self, guest_password):
        """
        Set the guest password
        :param guest_password: The guest password
        """
        self.guest_password = guest_password

    def set_vm_path(self, vm_path):
        """
        Set the path to the vm
        :param vm_path: The path to the vm
        """
        self.vm_path = vm_path

    def _run_command(self, command, vm_path, options=None):
        cmd = [self.vmrun_path]
        if self.host_type:
            cmd.extend(["-T", self.host_type])
        if self.vm_password:
            cmd.extend(["-vp", self.vm_password])
        if self.guest_user:
            cmd.extend(["-gu", self.guest_user])
        if self.guest_password:
            cmd.extend(["-gp", self.guest_password])
        cmd.append(command)
        if vm_path:
            cmd.append(vm_path)
        if options:
            cmd.extend(options)
        try:
            with subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            ) as proc:
                stdout, stderr = proc.communicate()
                stdout = stdout.decode("utf-8").strip()
                stderr = stderr.decode("utf-8").strip()
                return {"return_code": proc.returncode, "output": stdout}
        except FileNotFoundError:
            return {"return_code": 2, "output": "File not found!"}

    @_provide_vm_path
    def start(self, vm_path=None, nogui=False):
        """
        Start the vm
        :param vm_path: The path to the vm
        :param nogui: Start the vm without gui
        :return: The return code and the output
        """
        options = ["nogui"] if nogui else ["gui"]
        return self._run_command("start", vm_path, options)

    @_provide_vm_path
    def stop(self, vm_path=None, hard=False):
        """
        Stop the vm
        :param vm_path: The path to the vm
        :param hard: Stop the vm hard
        :return: The return code and the output
        """
        options = ["hard"] if hard else ["soft"]
        return self._run_command("stop", vm_path, options)

    @_provide_vm_path
    def reset(self, vm_path=None, hard=False):
        """
        Reset the vm
        :param vm_path: The path to the vm
        :param hard: Reset the vm hard
        :return: The return code and the output
        """
        options = ["hard"] if hard else ["soft"]
        return self._run_command("reset", vm_path, options)

    @_provide_vm_path
    def suspend(self, vm_path=None, hard=False):
        """
        Suspend the vm
        :param vm_path: The path to the vm
        :param hard: Suspend the vm hard
        :return: The return code and the output
        """
        options = ["hard"] if hard else ["soft"]
        return self._run_command("suspend", vm_path, options)

    @_provide_vm_path
    def pause(self, vm_path=None):
        """
        Pause the vm
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        return self._run_command("pause", vm_path)

    @_provide_vm_path
    def unpause(self, vm_path=None):
        """
        Unpause the vm
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        return self._run_command("unpause", vm_path)

    @_provide_vm_path
    def list_snapshots(self, vm_path=None, show_tree=False):
        """
        List the snapshots of the vm
        :param vm_path: The path to the vm
        :param show_tree: Show the snapshot tree
        :return: The return code and the output
        """
        options = ["showTree"] if show_tree else []
        return self._run_command("listSnapshots", vm_path, options)

    @_provide_vm_path
    def snapshot(self, snapshot_name, vm_path=None):
        """
        Take a snapshot of the vm
        :param snapshot_name: The name of the snapshot
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [snapshot_name]
        return self._run_command("snapshot", vm_path, options)

    @_provide_vm_path
    def delete_snapshot(self, snapshot_name, vm_path=None, and_delete_children=False):
        """
        Delete a snapshot of the vm
        :param snapshot_name: The name of the snapshot
        :param vm_path: The path to the vm
        :param and_delete_children: Delete the children of the snapshot
        :return: The return code and the output
        """
        options = [snapshot_name]
        if and_delete_children:
            options.append("andDeleteChildren")
        return self._run_command("deleteSnapshot", vm_path, options)

    @_provide_vm_path
    def revert_to_snapshot(self, snapshot_name, vm_path=None):
        """
        Revert to a snapshot of the vm
        :param snapshot_name: The name of the snapshot
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [snapshot_name]
        return self._run_command("revertToSnapshot", vm_path, options)

    @_provide_vm_path
    def list_network_adapters(self, vm_path=None):
        """
        List the network adapters of the vm
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        return self._run_command("listNetworkAdapters", vm_path)

    @_provide_vm_path
    def add_network_adapter(self, adapter_type, host_network=None, vm_path=None):
        """
        Add a network adapter to the vm
        :param adapter_type: The type of the adapter
        :param host_network: The host network
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [adapter_type]
        if host_network:
            options.append(host_network)
        return self._run_command("addNetworkAdapter", vm_path, options)

    @_provide_vm_path
    def set_network_adapter(
        self, adapter_index, adapter_type, host_network=None, vm_path=None
    ):
        """
        Set a network adapter of the vm
        :param adapter_index: The index of the adapter
        :param adapter_type: The type of the adapter
        :param host_network: The host network
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [str(adapter_index), adapter_type]
        if host_network:
            options.append(host_network)
        return self._run_command("setNetworkAdapter", vm_path, options)

    @_provide_vm_path
    def delete_network_adapter(self, adapter_index, vm_path=None):
        """
        Delete a network adapter of the vm
        :param adapter_index: The index of the adapter
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [str(adapter_index)]
        return self._run_command("deleteNetworkAdapter", vm_path, options)

    def list_host_networks(self):
        """
        List the host networks
        :return: The return code and the output
        """
        return self._run_command("listHostNetworks", None)

    def list_port_forwardings(self, host_network_name):
        """
        List the port forwardings
        :param host_network_name: The name of the host network
        :return: The return code and the output
        """
        return self._run_command("listPortForwardings", host_network_name)

    def set_port_forwarding(
        self,
        host_network_name,
        protocol,
        host_port,
        guest_ip,
        guest_port,
        description=None,
    ):
        """
        Set port forwarding
        :param host_network_name: The name of the host network
        :param protocol: The protocol
        :param host_port: The host port
        :param guest_ip: The guest ip
        :param guest_port: The guest port
        :param description: The description
        :return: The return code and the output
        """
        options = [protocol, str(host_port), guest_ip, str(guest_port)]
        if description:
            options.append(description)
        return self._run_command("setPortForwarding", host_network_name, options)

    def delete_port_forwarding(self, host_network_name, protocol, host_port):
        """
        Delete port forwarding
        :param host_network_name: The name of the host network
        :param protocol: The protocol
        :param host_port: The host port
        :return: The return code and the output
        """
        options = [protocol, str(host_port)]
        return self._run_command("deletePortForwarding", host_network_name, options)

    @_provide_vm_path
    def run_program_in_guest(
        self,
        program_path,
        no_wait=False,
        active_window=False,
        interactive=False,
        program_arguments=None,
        vm_path=None,
    ):
        """
        Run a program in the guest
        :param program_path: The path to the program
        :param no_wait: Do not wait for the program to finish
        :param active_window: Run the program in an active window
        :param interactive: Run the program interactively
        :param program_arguments: The arguments of the program
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = []
        if no_wait:
            options.append("-noWait")
        if active_window:
            options.append("-activeWindow")
        if interactive:
            options.append("-interactive")
        options.append(program_path)
        if program_arguments:
            options.extend(program_arguments)
        return self._run_command("runProgramInGuest", vm_path, options)

    @_provide_vm_path
    def file_exists_in_guest(self, file_path, vm_path=None):
        """
        Check if a file exists in the guest
        :param file_path: The path to the file in vm
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [file_path]
        return self._run_command("fileExistsInGuest", vm_path, options)

    @_provide_vm_path
    def directory_exists_in_guest(self, directory_path, vm_path=None):
        """
        Check if a directory exists in the guest
        :param directory_path: The path to the directory in vm
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [directory_path]
        return self._run_command("directoryExistsInGuest", vm_path, options)

    @_provide_vm_path
    def set_shared_folder_state(self, share_name, host_path, mode, vm_path=None):
        """
        Set the state of a shared folder
        :param share_name: The name of the share
        :param host_path: The path to the host
        :param mode: The mode
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [share_name, host_path, mode]
        return self._run_command("setSharedFolderState", vm_path, options)

    @_provide_vm_path
    def add_shared_folder(self, share_name, host_path, vm_path=None):
        """
        Add a shared folder to the vm
        :param share_name: The name of the share
        :param host_path: The path to the host
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [share_name, host_path]
        return self._run_command("addSharedFolder", vm_path, options)

    @_provide_vm_path
    def remove_shared_folder(self, share_name, vm_path=None):
        """
        Remove a shared folder from the vm
        :param share_name: The name of the share
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [share_name]
        return self._run_command("removeSharedFolder", vm_path, options)

    @_provide_vm_path
    def enable_shared_folders(self, runtime=False, vm_path=None):
        """
        Enable shared folders
        :param runtime: Enable shared folders at runtime
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = ["runtime"] if runtime else []
        return self._run_command("enableSharedFolders", vm_path, options)

    @_provide_vm_path
    def disable_shared_folders(self, runtime=False, vm_path=None):
        """
        Disable shared folders
        :param runtime: Disable shared folders at runtime
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = ["runtime"] if runtime else []
        return self._run_command("disableSharedFolders", vm_path, options)

    @_provide_vm_path
    def list_processes_in_guest(self, vm_path=None):
        """
        List the processes in the guest VM.

        :param vm_path: The path to the VM
        :return: A list of dictionaries containing process information {pid: {owner, cmd}}, or an error dictionary
        """
        output = self._run_command("listProcessesInGuest", vm_path)

        if output["return_code"] != 0:
            return output

        processes = {}
        for line in output["output"].splitlines()[1:]:
            try:
                pid, owner, cmd = [item.split("=")[1] for item in line.split(", ")]
                processes.update({pid: {"owner": owner, "cmd": cmd}})
            except (ValueError, IndexError) as e:
                continue

        return processes

    @_provide_vm_path
    def get_process_by_id(self, process_id, vm_path=None):
        """
        Get a process by its id
        :param process_id: The id of the process
        :param vm_path: The path to the vm
        :return: The process {owner, cmd} or None
        """
        process_id = str(process_id)
        if self.vm_path:
            processes = self.list_processes_in_guest()
        else:
            processes = self.list_processes_in_guest(vm_path)

        if processes and process_id in processes:
            return processes[process_id]
        return None

    @_provide_vm_path
    def kill_process_in_guest(self, process_id, vm_path=None):
        """
        Kill a process in the guest
        :param process_id: The id of the process
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [str(process_id)]
        return self._run_command("killProcessInGuest", vm_path, options)

    @_provide_vm_path
    def run_script_in_guest(
        self,
        interpreter_path,
        script_text,
        no_wait=False,
        active_window=False,
        interactive=False,
        vm_path=None,
    ):
        """
        Run a script in the guest
        :param interpreter_path: The path to the interpreter
        :param script_text: The text of the script
        :param no_wait: Do not wait for the program to finish
        :param active_window: Run the program in an active window
        :param interactive: Run the program interactively
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = []
        if no_wait:
            options.append("-noWait")
        if active_window:
            options.append("-activeWindow")
        if interactive:
            options.append("-interactive")
        options.extend([interpreter_path, script_text])
        return self._run_command("runScriptInGuest", vm_path, options)

    @_provide_vm_path
    def delete_file_in_guest(self, file_path, vm_path=None):
        """
        Delete a file in the guest
        :param file_path: The path to the file in vm
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [file_path]
        return self._run_command("deleteFileInGuest", vm_path, options)

    @_provide_vm_path
    def create_directory_in_guest(self, directory_path, vm_path=None):
        """
        Create a directory in the guest
        :param directory_path: The path to the directory in vm
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [directory_path]
        return self._run_command("createDirectoryInGuest", vm_path, options)

    @_provide_vm_path
    def delete_directory_in_guest(self, directory_path, vm_path=None):
        """
        Delete a directory in the guest
        :param directory_path: The path to the directory in vm
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [directory_path]
        return self._run_command("deleteDirectoryInGuest", vm_path, options)

    @_provide_vm_path
    def create_temp_file_in_guest(self, vm_path=None):
        """
        Create a temporary file in the guest
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        return self._run_command("createTempfileInGuest", vm_path)

    @_provide_vm_path
    def list_directory_in_guest(self, directory_path, vm_path=None):
        """
        List the directory in the guest
        :param directory_path: The path to the directory in vm
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [directory_path]
        return self._run_command("listDirectoryInGuest", vm_path, options)

    @_provide_vm_path
    def copy_file_from_host_to_guest(self, host_path, guest_path, vm_path=None):
        """
        Copy a file from the host to the guest
        :param host_path: The path to the file in host
        :param guest_path: The path to the file in guest
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [host_path, guest_path]
        return self._run_command("CopyFileFromHostToGuest", vm_path, options)

    @_provide_vm_path
    def copy_file_from_guest_to_host(self, guest_path, host_path, vm_path=None):
        """
        Copy a file from the guest to the host
        :param guest_path: The path to the file in guest
        :param host_path: The path to the file in host
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [guest_path, host_path]
        return self._run_command("CopyFileFromGuestToHost", vm_path, options)

    @_provide_vm_path
    def rename_file_in_guest(self, original_name, new_name, vm_path=None):
        """
        Rename a file in the guest
        :param original_name: The original name of the file
        :param new_name: The new name of the file
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [original_name, new_name]
        return self._run_command("renameFileInGuest", vm_path, options)

    @_provide_vm_path
    def type_keystrokes_in_guest(self, keystroke_string, vm_path=None):
        """
        Type keystrokes in the guest
        :param keystroke_string: The string of keystrokes
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [keystroke_string]
        return self._run_command("typeKeystrokesInGuest", vm_path, options)

    @_provide_vm_path
    def connect_named_device(self, device_name, vm_path=None):
        """
        Connect a named device
        :param device_name: The name of the device
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [device_name]
        return self._run_command("connectNamedDevice", vm_path, options)

    @_provide_vm_path
    def disconnect_named_device(self, vm_path, device_name):
        """
        Disconnect a named device
        :param device_name: The name of the device
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [device_name]
        return self._run_command("disconnectNamedDevice", vm_path, options)

    @_provide_vm_path
    def capture_screen(self, host_path, vm_path=None):
        """
        Capture the screen
        :param host_path: The path to the host
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [host_path]
        return self._run_command("captureScreen", vm_path, options)

    @_provide_vm_path
    def write_variable(
        self, variable_type, variable_name, variable_value, vm_path=None
    ):
        """
        Write a variable in the guest
        :param variable_type: The type of the variable
        :param variable_name: The name of the variable
        :param variable_value: The value of the variable
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [variable_type, variable_name, variable_value]
        return self._run_command("writeVariable", vm_path, options)

    @_provide_vm_path
    def read_variable(self, variable_type, variable_name, vm_path=None):
        """
        Read a variable in the guest
        :param variable_type: The type of the variable
        :param variable_name: The name of the variable
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [variable_type, variable_name]
        return self._run_command("readVariable", vm_path, options)

    @_provide_vm_path
    def get_guest_ip_address(self, wait=False, vm_path=None):
        """
        Get the guest IP address
        :param wait: Wait for the IP address
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = ["-wait"] if wait else []
        return self._run_command("getGuestIPAddress", vm_path, options)

    def list(self):
        """
        List all the VMs
        :return: The return code and the output
        """
        return self._run_command("list", None)

    @_provide_vm_path
    def upgrade_vm(self, vm_path=None):
        """
        Upgrade the VM
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        return self._run_command("upgradevm", vm_path)

    @_provide_vm_path
    def install_tools(self, vm_path=None):
        """
        Install the tools
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        return self._run_command("installTools", vm_path)

    @_provide_vm_path
    def check_tools_state(self, vm_path=None):
        """
        Check the tools state
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        return self._run_command("checkToolsState", vm_path)

    @_provide_vm_path
    def delete_vm(self, vm_path=None):
        """
        Delete the VM
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        return self._run_command("deleteVM", vm_path)

    @_provide_vm_path
    def clone(
        self, destination_path, clone_type, snapshot=None, clone_name=None, vm_path=None
    ):
        """
        Clone the VM
        :param destination_path: The path to the destination
        :param clone_type: The type of the clone
        :param snapshot: The snapshot
        :param clone_name: The name of the clone
        :param vm_path: The path to the vm
        :return: The return code and the output
        """
        options = [destination_path, clone_type]
        if snapshot:
            options.extend(["-snapshot", snapshot])
        if clone_name:
            options.extend(["-cloneName", clone_name])
        return self._run_command("clone", vm_path, options)

    def download_photon_vm(self, destination_path):
        """
        Download the photon VM
        :param destination_path: The path to the destination
        :return: The return code and the output
        """
        return self._run_command("downloadPhotonVM", destination_path)
