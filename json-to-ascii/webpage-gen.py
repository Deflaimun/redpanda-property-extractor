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

intro = "= Broker Configuration Properties \n:description: Broker configuration properties list. \n\nBroker configuration properties are applied individually to each broker in a cluster. \n\nIMPORTANT: After you change a broker-level property setting, you must restart the broker for the change to take effect. \n\nTo learn how to set these properties from studying a sample configuration file, see the xref:./node-configuration-sample.adoc[broker configuration sample].\n\n---\n\n"
yaml_config_start = "[,yaml]\n----\n"
yaml_config_end = "----"
output_content = intro
output_properties = ""
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
if properties is not None:
    total_properties = len(properties)
    # Write each property on a separate line
    for key, value in properties.items():
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
        if any(field is None for field in [value.get("description"), key, value.get("nullable"), value.get("type"), value.get("visibility")]):
            continue

        #have max but dont have min    
        if (value.get("maximum")) is not None:
            if(value.get("minimum")) is None:
                max_without_min+=key+"\n"
        #have max but dont have min  
        if (value.get("minimum")) is not None:
            if(value.get("maximum")) is None:
                min_without_max+=key+"\n"

        output_properties += (f"== {key}\n\n")
        output_properties += value.get("description") + "\n\n"
        output_properties += "*Requires Restart:* " + ("Yes" if value.get("needs_restart", False) else "No") + "\n\n"
        output_properties += "*Nullable:* " + ("Yes" if value.get("nullable", False) else "No") + "\n\n"
        output_properties += "*Visibility:* " + (value.get("visibility")) + "\n\n"
        output_properties += "*Type:* " + (value.get("type")) + "\n\n"
        if value.get('maximum') is not None and value.get('minimum') is not None:
            output_properties += "*Accepted values:* " + "[%d, %d]\n\n" % (value.get("minimum"), value.get("maximum"))

        output_properties += "*Default:* %r\n\n" % value.get("default")

        # hard todo
        
        output_properties += "*Example:* "+ "\n\n"



try:
    with open(os.path.join(output_path, output_file), "w+") as output:
        output.write(output_content + output_properties)
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
