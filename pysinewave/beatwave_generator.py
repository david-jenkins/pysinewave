import numpy as np

from pysinewave import utilities

class BeatWaveGenerator:
    '''Generates continuous sine wave data that smoothly transitions between pitches and volumes. 
    (For simplicity, use SineWave instead. 
    SineWaveGenerator is included to allow for alternative uses of generated sinewave data.)'''

    def __init__(self, pitch, beat_frequency, pitch_per_second=12, decibels=1, decibels_per_second=1,
                samplerate=utilities.DEFAULT_SAMPLE_RATE):
        self.frequency = utilities.pitch_to_frequency(pitch)
        self.beat_frequency = beat_frequency
        self.f1 = self.frequency-self.beat_frequency/2
        self.f2 = self.frequency+self.beat_frequency/2
        self.phase1 = 0
        self.phase2 = 0
        self.amplitude = utilities.decibels_to_amplitude_ratio(decibels)

        self.pitch_per_second = pitch_per_second
        self.decibels_per_second = decibels_per_second
        self.goal_f1 = self.f1
        self.goal_f2 = self.f2
        self.goal_amplitude = self.amplitude
        self.samplerate = samplerate
    
    def new_beat_frequency_arrays(self, time_array):
        '''Calcululate the frequency values for the next chunk of data.'''
        dir1 = utilities.direction(self.f1, self.goal_f1)
        new_frequency1 = self.f1 * utilities.interval_to_frequency_ratio(
                            dir1 * self.pitch_per_second * time_array)
        dir2 = utilities.direction(self.f2, self.goal_f2)
        new_frequency2 = self.f2 * utilities.interval_to_frequency_ratio(
                            dir2 * self.pitch_per_second * time_array)
        return utilities.bounded_by_end(new_frequency1, self.f1, self.goal_f1), utilities.bounded_by_end(new_frequency2, self.f2, self.goal_f2)

    def new_amplitude_array(self, time_array):
        '''Calcululate the amplitude values for the next chunk of data.'''
        dir = utilities.direction(self.amplitude, self.goal_amplitude)
        new_amplitude = self.amplitude * utilities.decibels_to_amplitude_ratio(
                            dir * self.decibels_per_second * time_array)
        return utilities.bounded_by_end(new_amplitude, self.amplitude, self.goal_amplitude)

    def new_phase_arrays(self, new_frequency_arrays, delta_time):
        '''Calcululate the phase values for the next chunk of data, given frequency values'''
        return self.phase1 + np.cumsum(new_frequency_arrays[0] * delta_time), self.phase2 + np.cumsum(new_frequency_arrays[1] * delta_time)

    def set_frequency(self, frequency):
        '''Set the goal frequency that the sinewave will gradually shift towards.'''
        self.goal_f1 = frequency-self.beat_frequency/2
        self.goal_f2 = frequency+self.beat_frequency/2

    def reset_frequency(self, frequency):
        '''Set the goal frequency that the sinewave will gradually shift towards.'''
        self.f1 = frequency-self.beat_frequency/2
        self.f2 = frequency+self.beat_frequency/2
        self.set_frequency(frequency)

    def set_beat_frequency(self, beat_frequency):
        self.beat_frequency = beat_frequency
        self.goal_f1 = self.frequency-beat_frequency/2
        self.goal_f2 = self.frequency+beat_frequency/2
    
    def set_pitch(self, pitch):
        '''Set the goal pitch that the sinewave will gradually shift towards.'''
        self.set_frequency(utilities.pitch_to_frequency(pitch))

    def reset_pitch(self, pitch):
        '''Set the goal pitch that the sinewave will gradually shift towards.'''
        self.reset_frequency(utilities.pitch_to_frequency(pitch))

    def set_amplitude(self, amplitude):
        '''Set the amplitude that the sinewave will gradually shift towards.'''
        self.goal_amplitude = amplitude
    
    def set_decibels(self, decibels):
        '''Set the amplitude (in decibels) that the sinewave will gradually shift towards.'''
        self.goal_amplitude = utilities.decibels_to_amplitude_ratio(decibels)
    
    def reset_decibels(self, decibels):
        '''Set the amplitude (in decibels) that the sinewave will gradually shift towards.'''
        self.amplitude = utilities.decibels_to_amplitude_ratio(decibels)
        self.goal_amplitude = self.amplitude

    def next_data(self, frames):
        '''Get the next pressure array for the given number of frames'''

        # Convert frame information to time information
        time_array = utilities.frames_to_time_array(0, frames, self.samplerate)
        delta_time = time_array[1] - time_array[0]

        # Calculate the frequencies of this batch of data
        new_frequency_arrays = self.new_beat_frequency_arrays(time_array)

        # Calculate the phases
        new_phase_arrays = self.new_phase_arrays(new_frequency_arrays, delta_time)

        # Calculate the amplitudes
        new_amplitude_array = self.new_amplitude_array(time_array)

        # Create the sinewave array
        sinewave_array = 0.5 * new_amplitude_array * (np.sin(2*np.pi*new_phase_arrays[0])+np.sin(2*np.pi*new_phase_arrays[1]))

        # Update frequency and amplitude
        self.f1 = new_frequency_arrays[0][-1]
        self.f2 = new_frequency_arrays[1][-1]
        self.frequency = (self.f1+self.f2)/2
        self.amplitude = new_amplitude_array[-1]

        # Update phase (getting rid of extra cycles, so we don't eventually have an overflow error)
        self.phase1 = new_phase_arrays[0][-1] % 1
        self.phase2 = new_phase_arrays[1][-1] % 1

        #print('Frequency: {0} Phase: {1} Amplitude: {2}'.format(self.frequency, self.phase, self.amplitude))

        return sinewave_array