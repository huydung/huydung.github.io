#!/usr/bin/env ruby
# -*- coding: utf-8 -*-
require 'yaml'

# Read the config file with explicit UTF-8 encoding and binary mode to preserve everything
config_text = File.read('_config.yml', mode: 'rb:BOM|UTF-8:UTF-8')

# Make the replacements - use exact UTF-8 strings
config_text.gsub!("Hydejack is a boutique Jekyll theme for hackers, nerds, and academics,\r\n  with a focus on personal sites that are meant to impress.", "Personal website of Huy Dũng - father of two, production manager in video game, trainer at heart.")
config_text.gsub!('Striving for Effective Leadership and Management. In Video Games Production, Corporate Training, Parenting, and beyond. Production Manager @ Gameloft. MIB, PMP, PMOCP.', 'Father of Two. Production Manager @ Gameloft Hanoi. Educator at heart.')
config_text.gsub!('Documentation', 'Contact Me')
config_text.gsub!('/docs/', 'https://docs.google.com/forms/d/e/1FAIpQLSeYmMIn9eZgPpUE6J0SPeUaMPN5KABRE_al-GRZkD2mDeW-Vw/viewform')
config_text.gsub!('Be+Vietnam+Pro', "'Be Vietnam Pro'")
config_text.gsub!('font_heading:          Merriweather', "font_heading:          'Merriweather'")

# Write back with binary mode to preserve CRLF
File.write('_config.yml', config_text, mode: 'wb')

puts "Config updated successfully!"
