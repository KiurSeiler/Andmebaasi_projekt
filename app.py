from flask import Flask, render_template, request, redirect, url_for
import psycopg2

app = Flask(__name__)

db_config = {
    'dbname': 'Robotics components',
    'user': 'postgres',
    'password': '123',
    'host': 'localhost',
    'port': '8008'
}

def get_db_connection():
    conn = psycopg2.connect(**db_config)
    return conn

def format_details(type, detail_data):
    if type == 'SBC':
        return {
            "Component ID": detail_data[0],
            "Name": detail_data[1],
            "CPU Architecture": detail_data[2],
            "Clock Speed": f"{detail_data[3]} GHz",
            "Cores": detail_data[4],
            "RAM": f"{detail_data[5] // 1024} GB" if detail_data[5] >= 1024 else f"{detail_data[5]} MB",
            "Storage Options": detail_data[6],
            "GPIO Pins": detail_data[7],
            "USB Ports": detail_data[8],
            "Power Consumption": detail_data[9],
            "Description": detail_data[10]
        }
    elif type == 'Microcontroller':
        return {
            "Component ID": detail_data[0],
            "Name": detail_data[1],
            "Family": detail_data[2],
            "Clock Speed": f"{detail_data[3]} MHz",
            "Flash Memory": f"{detail_data[4]} KB",
            "GPIO Pins": detail_data[5],
            "PWM Channels": detail_data[6],
            "Communication Interfaces": detail_data[7],
            "Power Supply Requirements": detail_data[8],
            "Description": detail_data[9]
        }
    elif type == 'Motor Controller':
        return {
            "Component ID": detail_data[0],
            "Name": detail_data[1],
            "Type": detail_data[2],
            "Input Voltage Range": detail_data[3],
            "Current Rating": detail_data[4],
            "Number of Channels": detail_data[5],
            "Control Method": detail_data[6],
            "Supported Motor Types": detail_data[7]
        }
    elif type == 'Motor':
        return {
            "Component ID": detail_data[0],
            "Name": detail_data[1],
            "Motor Type": detail_data[2],
            "Rated Voltage": f"{detail_data[3]} V",
            "Current Draw": f"{detail_data[4]} A",
            "Torque": detail_data[5],
            "RPM": detail_data[6],
            "Gear Ratio": detail_data[7] if detail_data[7] else "N/A",
            "Additional Information": detail_data[8]
        }
    elif type == 'Sensor':
        return {
            "Component ID": detail_data[0],
            "Name": detail_data[1],
            "Sensor Type": detail_data[2],
            "Measurement Range": detail_data[3],
            "Accuracy": detail_data[4],
            "Response Time": detail_data[5],
            "Operating Voltage": detail_data[6],
            "Communication Protocol": detail_data[7],
            "Output Type": detail_data[8]
        }
    elif type == 'Module':
        return {
            "Component ID": detail_data[0],
            "Name": detail_data[1],
            "Type": detail_data[2],
            "Protocol": detail_data[3],
            "Data Rate": detail_data[4],
            "Communication Range": detail_data[5],
            "Supported Voltage": detail_data[6],
            "Power Consumption": detail_data[7],
            "Additional Info": detail_data[8]
        }
    return {}

@app.route('/')
def index():
    query = request.args.get('search', '').strip().lower()
    
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if query:
        cursor.execute("""
            SELECT component_id, name, type, quantity, in_use
            FROM components
            WHERE LOWER(name) LIKE %s OR LOWER(type) LIKE %s
        """, (f'%{query}%', f'%{query}%'))
    else:
        cursor.execute("SELECT component_id, name, type, quantity, in_use FROM components")
    
    components = cursor.fetchall()
    
    cursor.execute("SELECT project_id, name FROM projects")
    projects = cursor.fetchall()
    
    details = {}

    for component in components:
        component_id, name, type, quantity, in_use = component
        if type == 'SBC':
            cursor.execute("SELECT * FROM sbc WHERE component_id = %s", (component_id,))
        elif type == 'Microcontroller':
            cursor.execute("SELECT * FROM microcontrollers WHERE component_id = %s", (component_id,))
        elif type == 'Motor Controller':
            cursor.execute("SELECT * FROM motor_controllers WHERE component_id = %s", (component_id,))
        elif type == 'Motor':
            cursor.execute("SELECT * FROM motors WHERE component_id = %s", (component_id,))
        elif type == 'Sensor':
            cursor.execute("SELECT * FROM sensors WHERE component_id = %s", (component_id,))
        elif type == 'Module':
            cursor.execute("SELECT * FROM modules WHERE component_id = %s", (component_id,))
        
        detail_data = cursor.fetchone()
        if detail_data:
            details[component_id] = format_details(type, detail_data)
    
    cursor.close()
    conn.close()

    return render_template('index.html', components=components, details=details, projects=projects, query=query)

@app.route('/add_component', methods=['POST'])
def add_component():
    conn = get_db_connection()
    cursor = conn.cursor()

    component_type = request.form['type']
    name = request.form['name']
    
    if component_type == 'SBC':
        cpu_architecture = request.form.get('cpu_architecture')
        clock_speed = request.form.get('clock_speed')
        cores = request.form.get('cores')
        ram_size = request.form.get('ram_size')
        storage_options = request.form.get('storage_options')
        gpio_pins = request.form.get('gpio_pins')
        usb_ports = request.form.get('usb_ports')
        power_consumption = request.form.get('power_consumption')
        description = request.form.get('description')
        
        cursor.execute("""
            INSERT INTO sbc (name, cpu_architecture, clock_speed, cores, ram_size, storage_options, gpio_pins, usb_ports, power_consumption, description)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
              (name, cpu_architecture, clock_speed, cores, ram_size, storage_options, gpio_pins, usb_ports, power_consumption, description))
    
    elif component_type == 'Microcontroller':
        family = request.form.get('family')
        clock_speed = request.form.get('clock_speed')
        flash_memory = request.form.get('flash_memory')
        gpio_pins = request.form.get('gpio_pins')
        pwm_channels = request.form.get('pwm_channels')
        comms_interfaces = request.form.get('comms_interfaces')
        power_supply = request.form.get('power_supply')
        
        cursor.execute("""
            INSERT INTO microcontrollers (name, family, clock_speed, flash_memory, gpio_pins, pwm_channels, comms_interfaces, power_supply)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
              (name, family, clock_speed, flash_memory, gpio_pins, pwm_channels, comms_interfaces, power_supply))

    elif component_type == 'Motor Controller':
        controller_type = request.form.get('type')
        input_voltage_range = request.form.get('input_voltage_range')
        current_rating = request.form.get('current_rating')
        channels = request.form.get('number_of_channels')
        control_method = request.form.get('control_method')
        supported_motors = request.form.get('supported_motor_types')
        
        cursor.execute("""
            INSERT INTO motor_controllers (name, type, input_voltage_range, current_rating, number_of_channels, control_method, supported_motor_types)
            VALUES (%s, %s, %s, %s, %s, %s, %s)""",
              (name, controller_type, input_voltage_range, current_rating, channels, control_method, supported_motors))

    elif component_type == 'Motor':
        motor_type = request.form.get('motor_type')
        rated_voltage = request.form.get('rated_voltage')
        current_draw = request.form.get('current_draw')
        torque = request.form.get('torque')
        rpm = request.form.get('rpm')
        gear_ratio = request.form.get('gear_ratio')
        additional_info = request.form.get('additional_info')
        
        cursor.execute("""
            INSERT INTO motors (name, motor_type, rated_voltage, current_draw, torque, rpm, gear_ratio, additional_info)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
              (name, motor_type, rated_voltage, current_draw, torque, rpm, gear_ratio, additional_info))

    elif component_type == 'Sensor':
        sensor_type = request.form.get('sensor_type')
        measurement_range = request.form.get('measurement_range')
        accuracy = request.form.get('accuracy')
        response_time = request.form.get('response_time')
        operating_voltage = request.form.get('operating_voltage')
        comms_protocol = request.form.get('comms_protocol')
        output_type = request.form.get('output_type')
        
        cursor.execute("""
            INSERT INTO sensors (name, sensor_type, measurement_range, accuracy, response_time, operating_voltage, comms_protocol, output_type)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
              (name, sensor_type, measurement_range, accuracy, response_time, operating_voltage, comms_protocol, output_type))

    elif component_type == 'Module':
        module_type = request.form.get('module_type')
        protocol = request.form.get('protocol')
        data_rate = request.form.get('data_rate')
        communication_range = request.form.get('communication_range')
        supported_voltage = request.form.get('supported_voltage')
        power_consumption = request.form.get('power_consumption')
        additional_info = request.form.get('additional_info')
        
        cursor.execute("""
            INSERT INTO modules (name, type, protocol, data_rate, communication_range, supported_voltage, power_consumption, additional_info)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
              (name, module_type, protocol, data_rate, communication_range, supported_voltage, power_consumption, additional_info))


    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('index'))


@app.route('/assign_to_project', methods=['POST'])
def assign_to_project():
    project_id = request.form['project_id']
    component_id = request.form['component_id']
    quantity = int(request.form['quantity'])

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO project_components (project_id, component_id, quantity)
        VALUES (%s, %s, %s)
    """, (project_id, component_id, quantity))

    cursor.execute("""
        UPDATE components SET in_use = TRUE
        WHERE component_id = %s
    """, (component_id,))

    conn.commit()
    cursor.close()
    conn.close()

    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
