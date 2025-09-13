% Define the input text as a multiline string
input_text = fileread('St. Joseph To Beatrice.txt');  % Assuming the text is saved in a file named 'coordinates.txt'

% Split the input text into lines
lines = strsplit(input_text, '\n');

% Open a file to write the output
output_file = fopen('1St. Joseph To Beatrice.txt', 'w');
if output_file == -1
    error('Unable to open output file for writing');
end

% Process each line
for i = 1:length(lines)
    line = strtrim(lines{i});
    % Check if the line contains a coordinate (i.e., it contains two commas)
    if contains(line, ',')
        coords = strsplit(line, ',');
        if length(coords) >= 2
            formatted_line = [coords{2}, char(9), coords{1}];  % Latitude first, then longitude with tab separation
            fprintf(output_file, '%s\n', formatted_line);
        end
    end
end

% Close the file
fclose(output_file);
