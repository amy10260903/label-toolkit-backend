const Spectrum = WaveSurfer.create({
    container: '#waveform',
    backgroundColor: '#091230',
    waveColor: '#63b3e4',
    progressColor: '#df5032',
    cursorColor: '#cf7655',
    cursorWidth: 2,
    height: 160,
    hideScrollbar: false,
    minPxPerSec: 100,
    // barWidth: 2,
    // barHeight: 1,
    // barGap: null
    // plugins: [
    //     WaveSurfer.spectrogram.create({
    //         wavesurfer: Spectrum,
    //         container: "#wave-spectrogram",
    //         labels: true
    //     })
    // ]
});
// Spectrum.load('/assets/dataset/TW_TPE/TW_TPE_005.wav');
