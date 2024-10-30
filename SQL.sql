DROP TABLE IF EXISTS project_components;
DROP TABLE IF EXISTS projects;
DROP TABLE IF EXISTS components;
DROP TABLE IF EXISTS sbc;
DROP TABLE IF EXISTS microcontrollers;
DROP TABLE IF EXISTS motor_controllers;
DROP TABLE IF EXISTS motors;
DROP TABLE IF EXISTS sensors;
DROP TABLE IF EXISTS modules;

CREATE SEQUENCE global_component_id_seq;

CREATE TABLE components (
    component_id INTEGER PRIMARY KEY DEFAULT nextval('global_component_id_seq'),
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    in_use BOOLEAN DEFAULT FALSE,
    CONSTRAINT unique_name_type UNIQUE (name, type)
);

CREATE TABLE sbc (
    component_id INTEGER DEFAULT nextval('global_component_id_seq') PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    cpu_architecture VARCHAR(50),
    clock_speed DECIMAL(4, 2),
    cores INTEGER,
    ram_size INTEGER,
    storage_options VARCHAR(100),
    gpio_pins INTEGER,
    usb_ports VARCHAR(50),
    power_consumption VARCHAR(50),
    description TEXT
);

CREATE TABLE microcontrollers (
    component_id INTEGER DEFAULT nextval('global_component_id_seq') PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    family VARCHAR(100),
    clock_speed DECIMAL(5, 2),
    flash_memory INTEGER,
    gpio_pins INTEGER,
    pwm_channels INTEGER,
    comms_interfaces VARCHAR(100),
    power_supply_requirements VARCHAR(100),
    description TEXT
);

CREATE TABLE motor_controllers (
    component_id INTEGER DEFAULT nextval('global_component_id_seq') PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    input_voltage_range VARCHAR(50),
    current_rating VARCHAR(50),
    number_of_channels INTEGER,
    control_method VARCHAR(100),
    supported_motor_types VARCHAR(100)
);

CREATE TABLE motors (
    component_id INTEGER DEFAULT nextval('global_component_id_seq') PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    motor_type VARCHAR(50),
    rated_voltage DECIMAL(5, 2),
    current_draw DECIMAL(5, 2),
    torque VARCHAR(50),
    rpm INTEGER,
    gear_ratio VARCHAR(20),
    additional_info TEXT
);

CREATE TABLE sensors (
    component_id INTEGER DEFAULT nextval('global_component_id_seq') PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    sensor_type VARCHAR(50),
    measurement_range VARCHAR(100),
    accuracy VARCHAR(100),
    response_time VARCHAR(50),
    operating_voltage VARCHAR(20),
    comms_protocol VARCHAR(50),
    output_type VARCHAR(50)
);

CREATE TABLE modules (
    component_id INTEGER DEFAULT nextval('global_component_id_seq') PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    type VARCHAR(50),
    protocol VARCHAR(50),
    data_rate VARCHAR(50),
    communication_range VARCHAR(50),
    supported_voltage VARCHAR(20),
    power_consumption VARCHAR(50),
    additional_info TEXT
);

CREATE TABLE projects (
    project_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    start_date DATE DEFAULT CURRENT_DATE
);

CREATE TABLE project_components (
    project_component_id SERIAL PRIMARY KEY,
    project_id INTEGER REFERENCES projects(project_id) ON DELETE CASCADE,
    component_id INTEGER REFERENCES components(component_id) ON DELETE CASCADE,
    quantity INTEGER DEFAULT 1
);

CREATE OR REPLACE FUNCTION update_components_table()
RETURNS TRIGGER AS $$
DECLARE
    component_type TEXT;
BEGIN
    component_type := CASE TG_TABLE_NAME
        WHEN 'sbc' THEN 'SBC'
        WHEN 'microcontrollers' THEN 'Microcontroller'
        WHEN 'motor_controllers' THEN 'Motor Controller'
        WHEN 'motors' THEN 'Motor'
        WHEN 'sensors' THEN 'Sensor'
        WHEN 'modules' THEN 'Module'
    END;

    INSERT INTO components (component_id, name, type, quantity)
    VALUES (NEW.component_id, NEW.name, component_type, 1)
    ON CONFLICT (name, type)
    DO UPDATE SET quantity = components.quantity + 1;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER sbc_insert_trigger
AFTER INSERT ON sbc
FOR EACH ROW EXECUTE FUNCTION update_components_table();

CREATE TRIGGER microcontroller_insert_trigger
AFTER INSERT ON microcontrollers
FOR EACH ROW EXECUTE FUNCTION update_components_table();

CREATE TRIGGER motor_controller_insert_trigger
AFTER INSERT ON motor_controllers
FOR EACH ROW EXECUTE FUNCTION update_components_table();

CREATE TRIGGER motor_insert_trigger
AFTER INSERT ON motors
FOR EACH ROW EXECUTE FUNCTION update_components_table();

CREATE TRIGGER sensor_insert_trigger
AFTER INSERT ON sensors
FOR EACH ROW EXECUTE FUNCTION update_components_table();

CREATE TRIGGER module_insert_trigger
AFTER INSERT ON modules
FOR EACH ROW EXECUTE FUNCTION update_components_table();
