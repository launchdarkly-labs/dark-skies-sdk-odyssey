# 🔊 Sound Effects Guide for Dark Skies

## Sound File Locations
Place your sound files in the `assets/sounds/` directory with these exact names:

### Required Sound Files:
- `jump.wav` - Plays when the van jumps (spacebar pressed)
- `hit.wav` - Plays when hitting an obstacle
- `score.wav` - Plays when successfully passing through obstacles
- `game_over.wav` - Plays when the game ends
- `background.wav` - Background music (loops continuously)

## Supported Audio Formats:
- **WAV** (recommended) - Best compatibility
- **OGG** - Good compression, cross-platform
- **MP3** - Supported but may have licensing issues

## Audio Specifications:
- **Sample Rate**: 22050 Hz or 44100 Hz
- **Bit Depth**: 16-bit
- **Channels**: Mono or Stereo
- **Duration**: 
  - Sound effects: 0.5-3 seconds
  - Background music: 30 seconds to 2 minutes (will loop)

## Volume Controls:
- **M Key**: Toggle background music on/off during gameplay
- **Default Volumes**:
  - Sound effects: 70%
  - Background music: 50%

## Implementation Features:
✅ **Safe Loading**: Game works even if sound files are missing  
✅ **Error Handling**: Console messages show which sounds loaded successfully  
✅ **Volume Control**: Built-in volume management  
✅ **Background Music**: Automatic looping  
✅ **Sound Effects**: Triggered by game events  

## Creating Sound Effects:
1. **Jump Sound**: Short "whoosh" or "flap" sound
2. **Hit Sound**: "Crash", "bang", or "impact" sound  
3. **Score Sound**: "Ding", "chime", or "success" sound
4. **Game Over**: "Explosion", "fail", or dramatic sound
5. **Background**: Ambient space/sci-fi music

## Free Sound Resources:
- [Freesound.org](https://freesound.org) - Creative Commons sounds
- [Pixabay Audio](https://pixabay.com/music/) - Royalty-free music
- [Incompetech](https://incompetech.com) - Kevin MacLeod music
- [Opengameart.org](https://opengameart.org) - Game-specific assets

## Testing:
The game will print messages to the console showing which sounds loaded successfully. If sound files are missing, the game will continue to work normally without audio.