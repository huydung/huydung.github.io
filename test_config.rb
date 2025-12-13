require 'yaml'
config = YAML.load_file('_config.yml')
puts "Include list: #{config['include']}"
puts "Exclude list: #{config['exclude']}"
