% Read data from the text file
data = readmatrix('Coords2.txt');

% Extract latitude, longitude, and altitude (if needed)
latitude = data(:, 1);
longitude = data(:, 2);
% altitude = data(:, 3); % Uncomment this line if you want to use altitude

% Plot the coordinates on a map
figure
geoplot(latitude, longitude, 'o')
geobasemap streets

% Add title and labels
title('Geographic Coordinates') 
xlabel('Longitude')
ylabel('Latitude')

% Add numbers next to each point
hold on
for i = 1:length(latitude)
    text(latitude(i), longitude(i), sprintf('%d', i), 'FontSize', 90, 'Color', 'red');
end
hold off

% Customize the appearance
set(gca, 'FontSize', 12)
