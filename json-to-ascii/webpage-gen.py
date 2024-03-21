import json
import os

input_json_path = "gen/"
input_json_file = "properties-output.json"

output_path = "output/pages/"
output_file = "properties.adoc"


error_folder = "output/error"
error_file_description = "empty_description.txt"
error_file_nullable = "empty_nullable.txt"
error_file_type = "empty_type.txt"
error_file_visibility = "empty_visibility.txt"
error_file_max_without_min = "max_without_min.txt"
error_file_min_without_max = "min_without_max.txt"

file_deprecated_properties ="deprecated_properties.txt"
deprecated_properties =""

empty_description = ""
empty_nullable = ""
empty_type = ""
empty_visibility = ""
max_without_min = ""
min_without_max = ""

intro = "= Redpanda Configuration Properties \n:description: Redpanda configuration properties. \n\n"
broker_title = "== Broker\n\n"
schema_registry_title = "== Schema Registry\n\n"
pandaproxy_title = "== HTTP Proxy\n\n" 
kafka_client_title = "== Kafka Client\n\n"
cluster_config_title = "== Cluster Configuration\n\n"

broker_intro = "Broker configuration properties are applied individually to each broker in a cluster. \n\nIMPORTANT: After you change a broker-level property setting, you must restart the broker for the change to take effect. \n\n"
schema_registry_intro = "Schema Registry intro\n\n"
pandaproxy_intro = "HTTP Proxy intro\n\n" 
kafka_client_intro = "Kafka Client intro\n\n"
cluster_config_intro = "Cluster Configuration intro\n\n"

broker_properties = broker_title+broker_intro
schema_registry_properties = schema_registry_title + schema_registry_intro
pandaproxy_properties = pandaproxy_title + pandaproxy_intro
kafka_client_properties = kafka_client_title + kafka_client_intro
cluster_config_properties = cluster_config_title + cluster_config_intro


yaml_config_start = "[,yaml]\n----\n"
yaml_config_end = "----"
total_properties =0

try:
    with open(os.path.join(input_json_path, input_json_file), 'r') as json_file:
        data = json.load(json_file)
except FileNotFoundError:
    print(f"Error: The file '{input_json_file}' does not exist.")
    exit(1)
except json.JSONDecodeError as e:
    print(f"Error: Failed to parse JSON in '{input_json_file}': {str(e)}")
    exit(1)

properties = data.get("properties")
total_properties = len(properties)
if properties is not None:
    # Write each property on a separate line
    for key, value in properties.items():
        output_property=""
        if (value.get("is_deprecated") is True):
            deprecated_properties+=key+"\n"
            continue
        if value.get("description") is None:
            empty_description+=key+"\n"
        if value.get("nullable") is None:
            empty_nullable+=key+"\n"
        if value.get("type") is None:
            empty_type+=key+"\n"
        if value.get("visibility") is None:
            empty_visibility+=key+"\n"
        if any(field is None for field in [value.get("description"), key, value.get("nullable"), value.get("type")]):
            continue

        #have max but dont have min    
        if (value.get("maximum")) is not None:
            if(value.get("minimum")) is None:
                max_without_min+=key+"\n"
        #have max but dont have min  
        if (value.get("minimum")) is not None:
            if(value.get("maximum")) is None:
                min_without_max+=key+"\n"

        output_property += (f"=== {key}\n\n")
        output_property += value.get("description") + "\n\n"
        #all node_config require restart, regardless of original data
        if value.get("defined_in") == "src/v/config/node_config.cc":
            output_property += "*Requires Restart:* " +"Yes" +"\n\n"
        else:
            output_property += "*Requires Restart:* " + ("Yes" if value.get("needs_restart", False) else "No") + "\n\n"
        output_property += "*Nullable:* " + ("Yes" if value.get("nullable", False) else "No") + "\n\n"   
        if value.get("visibility") is None:
            visibility_text = "None"
        else:
            visibility_text = value.get("visibility")

        output_property += "*Visibility:* " + visibility_text + "\n\n"
        output_property += "*Type:* " + (value.get("type")) + "\n\n"
        if value.get('maximum') is not None and value.get('minimum') is not None:
            output_property += "*Accepted values:* " + "[%d, %d]\n\n" % (value.get("minimum"), value.get("maximum"))

        output_property += "*Default:* %r\n\n" % value.get("default")
        
        # hard todo
        #output_property += "*Example:* "+ "\n\n"
        if value.get("defined_in") == "src/v/config/node_config.cc":
            broker_properties+=output_property  
        elif value.get("defined_in") == "src/v/pandaproxy/schema_registry/configuration.cc":
            schema_registry_properties+=output_property 
        elif value.get("defined_in") == "src/v/pandaproxy/rest/configuration.cc":
            pandaproxy_properties+=output_property  
        elif value.get("defined_in") == "src/v/kafka/client/configuration.cc":
            kafka_client_properties+=output_property  
        elif value.get("defined_in") == "src/v/config/configuration.cc":
            cluster_config_properties+=output_property


final_page = intro + broker_properties + "\n\n"+ cluster_config_properties + "\n\n"+kafka_client_properties+"\n\n"+pandaproxy_properties+"\n\n"+schema_registry_properties
try:
    with open(os.path.join(output_path, output_file), "w+") as output:
        output.write(final_page)
except Exception as e:
    print(f"Error: Failed to write data to {output_file}: {str(e)}")
    exit(1)
print(f"Data from {input_json_file} has been written to {output_file} successfully.")
print(f"Total properties read {total_properties}")

def write_error_file(output_path, error_file, error_content):
    file_path = os.path.join(output_path, error_file)
    try:
        # Delete the existing file if it exists
        if os.path.exists(file_path):
            os.remove(file_path)
        # Write a new file if error_content is not None
        if error_content is not None and error_content != '':
            if error_content.endswith('\n'):
                error_content = error_content[:-1]
            with open(file_path, "w+") as output:
                output.write(error_content)
                error_count = len(error_content.split('\n'))
                if error_count > 0:
                    empty_name = error_file.replace("empty_", "").replace(".txt", "")
                    error_percentage = round((error_count / total_properties) * 100, 2)
                    print(f"You have {error_count} properties with empty {empty_name}. Percentage of errors {error_percentage}%. Data written in '{error_file}'.")
    except Exception as e:
        print(f"Error: Failed to write data to '{error_file}': {str(e)}")

write_error_file(error_folder,error_file_description,empty_description)
write_error_file(error_folder,error_file_nullable,empty_nullable)
write_error_file(error_folder,error_file_type,empty_type)
write_error_file(error_folder,error_file_visibility,empty_visibility)
write_error_file(error_folder,error_file_max_without_min,max_without_min)
write_error_file(error_folder,error_file_min_without_max,min_without_max)
write_error_file(error_folder,file_deprecated_properties,deprecated_properties)
