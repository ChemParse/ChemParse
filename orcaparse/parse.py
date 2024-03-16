import json
import re
import warnings

import numpy as np
import pandas as pd

numeric_const_pattern = '[-+]? (?: (?: \d* \. \d+ ) | (?: \d+ \.? ) )(?: [Ee] [+-]? \d+ ) ?'
rx = re.compile(numeric_const_pattern, re.VERBOSE)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


def get_last_occurrence(filename, bstring):
    with open(filename) as f:
        lines = f.readlines()
        for line in lines[::-1]:
            if line.startswith(bstring):
                return line
    return ''


#     parse the time string to give back the time as a float:
def parse_time(string):
    # print(f'{string = }')
    try:
        r = rx.findall(string)
        time = float(r[0])
    except Exception as e:
        # print(Exception)
        time = 0.0
    return time


def energy_from_ocra(filename):
    """
    Energy in Eh
    """
    with open(filename) as f:
        lines = f.readlines()
        for id, line in enumerate(lines[::-1]):
            if line.startswith('FINAL SINGLE POINT ENERGY'):
                break

        d = rx.findall(line)
        return float(d[0])


def energy_from_ocra_ev(filename):
    """
    Energy in eV
    """
    return EH_TO_EV*energy_from_ocra(filename)


def surface_energy_from_orca(filename, energy_type='Actual Energy'):
    """
    Extracts surface energy data from ORCA output file.

    Parameters:
    - filename: Name of the ORCA output file.
    - energy_type: Type of energy to extract. Can be 'Actual Energy' or 'SCF energy'.

    Returns:
    - DataFrame containing the extracted data.
    """
    data = []
    pattern = re.compile(r"(\d+\.\d+)\s+(-?\d+\.\d+)")

    with open(filename, 'r') as f:
        lines = f.readlines()

        # Find the starting line based on energy type, but search from the end
        start_line = next((len(lines) - 1 - i for i,
                          line in enumerate(reversed(lines)) if energy_type in line), None)
        if start_line is None:
            raise ValueError(f"'{energy_type}' not found in the file.")

        # Extract data
        for line in lines[start_line+1:]:
            if line.startswith('------------------') or len(line.strip()) == 0:
                break
            match = pattern.search(line)
            if match:
                param, e_eh = [float(val) for val in match.groups()]
                e_ev = e_eh * EH_TO_EV  # Convert from Hartree to eV
                data.append({'param': param, 'E(Eh)': e_eh, 'E(eV)': e_ev})

    return pd.DataFrame(data)


def orbital_energy_from_ocra(filename):
    data = pd.DataFrame()
    with open(filename) as f:
        lines = f.readlines()
        for id, line in enumerate(lines[::-1]):
            if line.startswith('ORBITAL ENERGIES'):
                break
        # print(f'{id = }')
        # print(f'{line = }')

        for line in lines[id + 4:]:
            if line.startswith('------------------') or len(line) <= 2:
                break
            d = rx.findall(line)
            data = pd.concat([data, pd.DataFrame({'NO': [float(d[0])], 'OCC': [float(
                d[1])], 'E(Eh)': [float(d[2])], 'E(eV)': [float(d[3])]})], ignore_index=True)

    return data


def neb_energy_from_ocra(filename):
    data = pd.DataFrame()
    with open(filename) as f:
        lines = f.readlines()
        file_key = 'error'
        for id, line in enumerate(lines[::-1]):
            if 'PATH SUMMARY' in line:
                file_key = 'CI'
                break
            if line.startswith('                      PATH SUMMARY'):
                file_key = 'TS'
                break
        id = len(lines) - id
        # print(f'{id = }')
        # print(f'{line = }')

        for i, line in enumerate(lines[id + 4:]):
            # print(f'{line = }')
            if line.startswith('--------') or len(line) <= 2:
                break
            if file_key == 'TS':
                d = rx.findall(line)
                if 'TS' in line:
                    data = pd.concat([data, pd.DataFrame({'Image': [i], 'E(Eh)': [float(d[0])], 'dE(kcal/mol)': [
                        float(d[1])], 'max(|Fp|)': [float(d[2])], 'RMS(Fp)': [float(d[3])], 'Comment': ['TS']})],
                        ignore_index=True)
                elif 'CI' in line:
                    data = pd.concat([data, pd.DataFrame({'Image': [i], 'E(Eh)': [float(d[1])], 'dE(kcal/mol)': [
                        float(d[2])], 'max(|Fp|)': [float(d[3])], 'RMS(Fp)': [float(d[4])], 'Comment': ['CI']})],
                        ignore_index=True)
                else:
                    data = pd.concat([data, pd.DataFrame({'Image': [i], 'E(Eh)': [float(d[1])], 'dE(kcal/mol)': [
                        float(d[2])], 'max(|Fp|)': [float(d[3])], 'RMS(Fp)': [float(d[4])], 'Comment': ['']})],
                        ignore_index=True)
            if file_key == 'CI':
                d = rx.findall(line)
                if 'CI' in line:
                    data = pd.concat([data, pd.DataFrame(
                        {'Image': [i], 'Dist.(Ang.)': [float(d[1])], 'E(Eh)': [float(d[2])], 'dE(kcal/mol)': [
                            float(d[3])], 'max(|Fp|)': [float(d[4])], 'RMS(Fp)': [float(d[5])], 'Comment': ['CI']})],
                        ignore_index=True)
                else:
                    data = pd.concat([data, pd.DataFrame(
                        {'Image': [i], 'Dist.(Ang.)': [float(d[1])], 'E(Eh)': [float(d[2])], 'dE(kcal/mol)': [
                            float(d[3])], 'max(|Fp|)': [float(d[4])], 'RMS(Fp)': [float(d[5])], 'Comment': ['']})],
                        ignore_index=True)

    data['Energy, eV'] = EH_TO_EV * (data['E(Eh)'] - data['E(Eh)'].iloc[0])

    return data


def neb_energy_from_ocra(filename):
    data = pd.DataFrame()
    try:
        with open(filename) as f:
            lines = f.readlines()
            file_key = 'error'
            for id, line in enumerate(lines[::-1]):
                if 'PATH SUMMARY FOR NEB-TS' in line:
                    file_key = 'TS'
                    break
                if 'PATH SUMMARY' in line:
                    file_key = 'CI'
                    break
            id = len(lines) - id
            # print(f'{id = }')
            # print(f'{line = }')
            # print(f'{file_key = }')

            for i, line in enumerate(lines[id + 4:]):
                # print(f'{line = }')
                if line.startswith('--------') or len(line) <= 2:
                    break
                if file_key == 'TS':
                    d = rx.findall(line)
                    if 'TS' in line:
                        data = pd.concat([data, pd.DataFrame({'Image': [i], 'E(Eh)': [float(d[0])], 'dE(kcal/mol)': [
                            float(d[1])], 'max(|Fp|)': [float(d[2])], 'RMS(Fp)': [float(d[3])], 'Comment': ['TS']})], ignore_index=True)
                    elif 'CI' in line:
                        data = pd.concat([data, pd.DataFrame({'Image': [i], 'E(Eh)': [float(d[1])], 'dE(kcal/mol)': [
                            float(d[2])], 'max(|Fp|)': [float(d[3])], 'RMS(Fp)': [float(d[4])], 'Comment': ['CI']})], ignore_index=True)
                    else:
                        data = pd.concat([data, pd.DataFrame({'Image': [i], 'E(Eh)': [float(d[1])], 'dE(kcal/mol)': [
                            float(d[2])], 'max(|Fp|)': [float(d[3])], 'RMS(Fp)': [float(d[4])], 'Comment': ['']})], ignore_index=True)
                if file_key == 'CI':
                    d = rx.findall(line)
                    if 'CI' in line:
                        data = pd.concat([data, pd.DataFrame({'Image': [i], 'Dist.(Ang.)': [float(d[1])], 'E(Eh)': [float(d[2])], 'dE(kcal/mol)': [
                            float(d[3])], 'max(|Fp|)': [float(d[4])], 'RMS(Fp)': [float(d[5])], 'Comment': ['CI']})], ignore_index=True)
                    else:
                        data = pd.concat([data, pd.DataFrame({'Image': [i], 'Dist.(Ang.)': [float(d[1])], 'E(Eh)': [float(d[2])], 'dE(kcal/mol)': [
                            float(d[3])], 'max(|Fp|)': [float(d[4])], 'RMS(Fp)': [float(d[5])], 'Comment': ['']})], ignore_index=True)

    except Exception as e:
        print(e)
        data = pd.DataFrame({'Image': [0], 'Dist.(Ang.)': [0.], 'E(Eh)': [np.nan], 'dE(kcal/mol)': [
            np.nan], 'max(|Fp|)': [np.nan], 'RMS(Fp)': [np.nan], 'Comment': ['']})
    data['Energy, eV'] = EH_TO_EV*(data['E(Eh)'])
    return data


def neb_energy_from_ocra_interp(filename):
    points = pd.DataFrame()
    interpolation = pd.DataFrame()
    try:
        with open(filename) as f:
            lines = f.readlines()
            for id, line in enumerate(lines):
                if 'Images' in line:
                    break
            # print(f'{id = }')
            # print(f'{line = }')

            for i, line in enumerate(lines[id + 1:]):
                # print(f'{line = }')
                if line.startswith('--------') or len(line) <= 2:
                    break

                d = rx.findall(line)
                points = pd.concat([points, pd.DataFrame({'Image': [i], 'Images': [float(d[0])], 'Distance (Bohr)': [
                    float(d[1])], 'Energy (Eh)': [float(d[2])]})], ignore_index=True)

            # print(f'{i = }')
            # print(f'{line = }')

            for j, line in enumerate(lines[id + i + 4:]):
                # print(f'{line = }')
                if line.startswith('--------') or len(line) <= 2:
                    break

                d = rx.findall(line)
                interpolation = pd.concat([interpolation, pd.DataFrame({'Interp': [float(d[0])], 'Distance (Bohr)': [
                    float(d[1])], 'Energy (Eh)': [float(d[2])]})], ignore_index=True)
    except Exception as e:
        print(e)
        points = pd.DataFrame({'Image': [0], 'Images': [0.], 'Distance (Bohr)': [
            0.], 'Energy (Eh)': [np.nan]})
        interpolation = pd.DataFrame({'Interp': [0.], 'Distance (Bohr)': [
            0.], 'Energy (Eh)': [np.nan]})

    points['Energy, eV'] = EH_TO_EV * \
        (points['Energy (Eh)']-points['Energy (Eh)'].iloc[0])
    interpolation['Energy, eV'] = EH_TO_EV * \
        (interpolation['Energy (Eh)']-interpolation['Energy (Eh)'].iloc[0])

    return points, interpolation


def neb_free_energy_from_ocra(filename):
    try:
        with open(filename) as f:
            lines = f.readlines()
            free_energy = np.nan
            for id, line in enumerate(lines[::-1]):
                if 'Final Gibbs free energy' in line:
                    d = rx.findall(line)
                    free_energy = float(d[-1])
                    break
    except Exception as e:
        print(e)
        return np.nan

    return EH_TO_EV*free_energy


def extract_total_scf_energy(filename):
    """
    Extracts the total energy value from the ORCA output text,
    specifically from the line that is three lines after "TOTAL SCF ENERGY".

    Parameters:
    filename (str): The name of the ORCA output file.

    Returns:
    float: The extracted total energy value, or None if not found.
    """
    try:
        with open(filename, 'r') as file:
            # Read the content of the file into a string
            content = file.read()

        # Split the content into lines
        lines = content.split('\n')

        # Initialize a variable to keep track of lines after "TOTAL SCF ENERGY"
        line_after_total_scf_energy = 0

        # Initialize a variable to store the total energy value
        total_energy = None

        # Iterate through the lines
        for line in lines:
            # Check if we're currently on the line that contains "TOTAL SCF ENERGY"
            if "TOTAL SCF ENERGY" in line:
                # Start counting lines after this
                line_after_total_scf_energy = 1
            elif line_after_total_scf_energy > 0:
                # Increment the counter if we're after the "TOTAL SCF ENERGY" line
                line_after_total_scf_energy += 1

                # Check if this is the third line after "TOTAL SCF ENERGY"
                if line_after_total_scf_energy == 4:
                    # Extract the total energy value
                    parts = line.split(':')
                    if len(parts) > 1:
                        try:
                            total_energy = float(parts[1].split()[0])
                        except ValueError:
                            # If conversion to float fails, return None
                            total_energy = None
                    break  # Exit the loop once the value is found

        return total_energy
    except FileNotFoundError:
        print(f"The file {filename} was not found.")
        return None
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")
        return None


def parse_orbital_data(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Find the line numbers for spin up and spin down sections
    spin_up_start = spin_down_start = None
    for i, line in enumerate(lines):
        if 'SPIN UP ORBITALS' in line:
            spin_up_start = i + 2  # Skip the header row
        elif 'SPIN DOWN ORBITALS' in line:
            spin_down_start = i + 2  # Skip the header row

    # Extract lines for spin up orbitals
    spin_up_lines = []
    for line in lines[spin_up_start:]:
        if line.strip() in ('' or '*Only the first 10 virtual orbitals were printed.'):
            break  # Stop at the first empty line
        spin_up_lines.append(line.split())

    # Extract lines for spin down orbitals
    spin_down_lines = []
    for line in lines[spin_down_start:]:
        if line.strip() in ('' or '*Only the first 10 virtual orbitals were printed.'):
            break  # Stop at the first empty line
        spin_down_lines.append(line.split())

    # Convert the extracted data into pandas DataFrames
    spin_up_df = pd.DataFrame(spin_up_lines, columns=[
                              'NO', 'OCC', 'E(Eh)', 'E(eV)'])
    spin_down_df = pd.DataFrame(spin_down_lines, columns=[
                                'NO', 'OCC', 'E(Eh)', 'E(eV)'])

    # Convert numeric columns to appropriate data types
    for df in (spin_up_df, spin_down_df):
        df['NO'] = pd.to_numeric(df['NO'])
        df['OCC'] = pd.to_numeric(df['OCC'])
        df['E(Eh)'] = pd.to_numeric(df['E(Eh)'])
        df['E(eV)'] = pd.to_numeric(df['E(eV)'])

    return spin_up_df, spin_down_df


def parse_single_orbital_data(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Find the line numbers for the orbital energies section
    orbital_start = None
    for i, line in enumerate(lines):
        if 'ORBITAL ENERGIES' in line:
            orbital_start = i + 4  # Skip the header rows

    # Extract lines for the orbitals
    orbital_lines = []
    for line in lines[orbital_start:]:
        if line.strip() == '' or 'Only the first 10 virtual orbitals were printed' in line:
            break  # Stop at the first empty line or the specified string
        orbital_lines.append(line.split())

    # Convert the extracted data into a pandas DataFrame
    orbital_df = pd.DataFrame(orbital_lines, columns=[
                              'NO', 'OCC', 'E(Eh)', 'E(eV)'])

    # Convert numeric columns to appropriate data types
    orbital_df['NO'] = pd.to_numeric(orbital_df['NO'])
    orbital_df['OCC'] = pd.to_numeric(orbital_df['OCC'])
    orbital_df['E(Eh)'] = pd.to_numeric(orbital_df['E(Eh)'])
    orbital_df['E(eV)'] = pd.to_numeric(orbital_df['E(eV)'])

    return orbital_df


def extract_dipole_magnitude_debye_from_file(filename):
    """
    Reads an ORCA output file and extracts the magnitude of the dipole moment in Debye.

    Parameters:
    filename (str): The path to the ORCA output file.

    Returns:
    float: The magnitude of the dipole moment in Debye, or None if not found.
    """
    try:
        with open(filename, 'r') as file:
            content = file.read()

        # Regular expression pattern to find the magnitude in Debye
        pattern = r"Magnitude \(Debye\) +: +([\d.]+)"

        # Search for the pattern in the content of the file
        match = re.search(pattern, content)

        # If a match is found, convert the matched string to a float and return it
        if match:
            return float(match.group(1))

    except FileNotFoundError:
        print(f"The file {filename} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # If no match is found or an error occurred, return None
    return None


def extract_scf_cycles_from_file(filename):
    """
    Reads an ORCA output file and extracts the number of SCF cycles.

    Parameters:
    filename (str): The path to the ORCA output file.

    Returns:
    int: The number of SCF cycles, or None if not found.
    """
    try:
        with open(filename, 'r') as file:
            content = file.read()

        # Regular expression pattern to find the SCF convergence line and extract the number of cycles
        pattern = r"SCF CONVERGED AFTER\s+(\d+)\s+CYCLES"

        # Search for the pattern in the content of the file
        match = re.search(pattern, content)

        # If a match is found, convert the captured number of cycles to an integer and return it
        if match:
            return int(match.group(1))

    except FileNotFoundError:
        print(f"The file {filename} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    # If no match is found or an error occurred, return None
    return None


def parse_td_dft_excited_states(filename):
    states_data = []

    with open(filename, 'r') as file:
        lines = file.readlines()

    state_number = None
    energy_ev = None
    transitions = []

    # Regular expression to match state lines and extract information
    state_pattern = re.compile(r"STATE\s+(\d+):.*?(\d+\.\d+)\s+eV")

    # Regular expression to match orbital transitions
    transition_pattern = re.compile(
        r"(\d+[ab])\s+->\s+(\d+[ab])\s+:\s+(\d+\.\d+)")

    for line in lines:
        # Check if the line is a state line
        state_match = state_pattern.search(line)
        if state_match:
            if state_number is not None:
                # Append the previous state's data before starting a new state
                states_data.append({
                    'State': state_number,
                    'Energy (eV)': energy_ev,
                    'Transitions': transitions
                })
                transitions = []  # Reset the transitions list for the next state

            # Start capturing data for the new state
            state_number = int(state_match.group(1))
            energy_ev = float(state_match.group(2))
        else:
            # If the line is not a state line, check for orbital transitions
            transition_match = transition_pattern.search(line)
            if transition_match:
                transitions.append({
                    'From Orbital': transition_match.group(1),
                    'To Orbital': transition_match.group(2),
                    'Coefficient': float(transition_match.group(3))
                })

    # Append the last state's data
    if state_number is not None:
        states_data.append({
            'State': state_number,
            'Energy (eV)': energy_ev,
            'Transitions': transitions
        })

    return states_data


def check_orca_terminated_normally(filename):
    with open(filename, 'r') as file:
        lines = file.readlines()  # Read all lines into a list

    # Iterate over the lines in reverse order
    for line in reversed(lines):
        if "****ORCA TERMINATED NORMALLY****" in line:
            return True
    return False
