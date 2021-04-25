%% Camera Settings for Bruker GigE Recordings

disp('Acquiring Camera');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Define the camera object through videoinput()
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% videoinput('adapter', index_of_cam, 'Datatype')
% In our case, we use:
%       'Adapter' = 'gige'
%       index_of_cam = 1; we only have one camera (for now...)
%       'Datatype' = 'Mono8'; monochromatic 8-bit images
camera = videoinput('gige', 1, 'Mono8');
disp('Camera Acquired');

disp('Acquiring Camera Source');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Define camera source with getselectedsource()
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% getselectedsource(video_acquisition_object)
% Here, it's the camera object we just defined
source = getselectedsource(camera);
disp('Camera Source Acquired');


disp('Setting Continuous Recording');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Set number of frames to acquire with 'FramesPerTrigger'
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% This is a writable parameter for the camera's settings
% For now, we want to have this acquire video until we tell it to stop.
% To do this, we use the MATLAB value of 'Inf'.
% This enables a continuous recording setting.
camera.FramesPerTrigger = Inf;
disp('Continuous Recording Set');


disp('Setting Output Line');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Set output line for TTL pulses coming off the camera with 'LineSelector'
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The Genie Nano has pinouts specified for each of the 4 lines
% Lines 1/2 are for inputs to the camera while Lines 3/4 are for outputs
% Our camera is using 'Line3' as its configuration
% We change this at the camera's 'source'
source.LineSelector = 'Line3';
disp('Output Line Set');


disp('Setting TTL Pulse Duration');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Set TTL pulse duration with 'outputLinePulseDuration'
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% TTL pulses are simply 'HIGH' signals sent from the camera
% By default, the amount of time the camera sends a 'HIGH' signal is 0 sec
% We need this to be set long enough to transmit clear signals to the DAQ
% A value of 3000us (microseconds) appears sufficient.
% We change this at the camera's 'source'
source.outputLinePulseDuration = 3000;
disp('TTL Pulse Duration Set');


disp('Setting Output Trigger');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Set ouput to pulse when a frame is acquired with 'outputLineSource'
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The camera needs to know when to send a TTL pulse
% We want it to send a pulse each time the camera acquires a frame
% Thus, we use 'PulseOnStartofFrame' as the parameter
% We change this at the camera's 'source'
source.outputLineSource = 'PulseOnStartofFrame';
disp('Output Trigger Set');


disp('Setting Logging Mode');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Define where the camera will collect/store frames with 'LoggingMode'
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The camera needs to know where it should send and store frames
% This property is known as its 'logging mode'
% Logging mode can be set to disk, memory, or both at once
% We'll log our frames to disk directly
% This is changed at the camera
camera.LoggingMode = 'disk';
disp('Logging Mode Set');


disp('Setting File Location');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Define location on disk frames are written to with 'VideoWriter'
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Now that the camera knows to write to disk, we need to provide a location
% That location is a specific file path and name we'll give the file.
% This is stored as the variable 'diskLogger'
% First, we need to know what the file should be called
% The user will define this for us when prompted

% Define prompt for the user and use entry as variable fileName
prompt = 'Enter file name and press Enter: ';
fileName = input(prompt, 's'); % use 's' to define input as a string

% Define filePath and append fileName to it
filePath = append('C:\Users\jdelahanty\Documents\MATLAB\', fileName);
disp('File Location Set');

% We also need to provide the filetype to write
% In our case, we'll write to a grayscaled .avi file
diskLogger = VideoWriter(filePath, 'Grayscale AVI');
disp('Video Writer Set');


disp('Set Camera Logging');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Set camera's 'DiskLogger' setting to 'diskLogger' defined above
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% The camera setting finally needs to be told where frames should go
camera.DiskLogger = diskLogger;
disp('Camera Logging Set');


disp('Displaying Preview');
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Initialize a preview of the camera for the user with 'preview()'
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Use preview(camera) to initialize a preview immediately
preview(camera)


% Display next steps for the user
disp('When ready, type:'); disp('start(camera)');
disp('When done, type:')
disp('1. stop(camera)'); disp('2. delete(camera)'); disp('3. clear all');