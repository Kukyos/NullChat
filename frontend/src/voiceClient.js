<<<<<<< Updated upstream
// Voice client utility for Sarvam placeholder endpoints
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

export async function voiceChat(blob, { language, sessionId } = {}) {
  const form = new FormData()
  form.append('file', blob, 'voice.webm')
  if (language) form.append('language', language)
  if (sessionId) form.append('session_id', sessionId)
  const res = await fetch(`${API_BASE}/voice/chat`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`voice/chat HTTP ${res.status}`)
=======
// Voice client utility for Sarvam real voice endpoints
// Adds client-side WebM/Opus -> WAV (PCM16 16kHz mono) conversion so the backend
// does NOT require ffmpeg to transcode. If conversion fails, original blob is sent.
const API_BASE = import.meta.env.VITE_API_BASE || 'http://127.0.0.1:8000'

// Target sample rate & channel config for STT service
const TARGET_SAMPLE_RATE = 16000

async function blobToArrayBuffer(blob) {
  return await blob.arrayBuffer()
}

function encodeWavFromFloat32(float32, sampleRate) {
  // Convert Float32Array [-1,1] to 16-bit PCM and add RIFF/WAV header
  const numSamples = float32.length
  const bytesPerSample = 2
  const blockAlign = bytesPerSample * 1 // mono
  const byteRate = sampleRate * blockAlign
  const buffer = new ArrayBuffer(44 + numSamples * bytesPerSample)
  const view = new DataView(buffer)

  // RIFF identifier 'RIFF'
  writeString(view, 0, 'RIFF')
  // file length minus 8
  view.setUint32(4, 36 + numSamples * bytesPerSample, true)
  // RIFF type 'WAVE'
  writeString(view, 8, 'WAVE')
  // format chunk identifier 'fmt '
  writeString(view, 12, 'fmt ')
  // format chunk length 16
  view.setUint32(16, 16, true)
  // sample format (raw)
  view.setUint16(20, 1, true)
  // channel count
  view.setUint16(22, 1, true)
  // sample rate
  view.setUint32(24, sampleRate, true)
  // byte rate (sample rate * block align)
  view.setUint32(28, byteRate, true)
  // block align (channel count * bytes per sample)
  view.setUint16(32, blockAlign, true)
  // bits per sample
  view.setUint16(34, 16, true)
  // data chunk identifier 'data'
  writeString(view, 36, 'data')
  // data chunk length
  view.setUint32(40, numSamples * bytesPerSample, true)

  // Write PCM samples
  let offset = 44
  for (let i = 0; i < numSamples; i++) {
    let s = Math.max(-1, Math.min(1, float32[i]))
    s = s < 0 ? s * 0x8000 : s * 0x7FFF
    view.setInt16(offset, s, true)
    offset += 2
  }
  return new Blob([buffer], { type: 'audio/wav' })
}

function writeString(view, offset, str) {
  for (let i = 0; i < str.length; i++) view.setUint8(offset + i, str.charCodeAt(i))
}

async function convertWebmBlobToWav(webmBlob) {
  try {
    const arrayBuffer = await blobToArrayBuffer(webmBlob)
    const audioCtx = new (window.AudioContext || window.webkitAudioContext)()
    const decoded = await audioCtx.decodeAudioData(arrayBuffer.slice(0))
    // Resample using OfflineAudioContext to target sample rate & mono
    const duration = decoded.duration
    const offline = new OfflineAudioContext(1, Math.ceil(TARGET_SAMPLE_RATE * duration), TARGET_SAMPLE_RATE)
    const source = offline.createBufferSource()
    // Mixdown to mono if needed
    let mixedBuffer
    if (decoded.numberOfChannels === 1) {
      mixedBuffer = decoded
    } else {
      // average channels
      const chData = []
      const frameCount = decoded.length
      for (let c = 0; c < decoded.numberOfChannels; c++) chData.push(decoded.getChannelData(c))
      const mono = new Float32Array(frameCount)
      for (let i = 0; i < frameCount; i++) {
        let sum = 0
        for (let c = 0; c < chData.length; c++) sum += chData[c][i]
        mono[i] = sum / chData.length
      }
      mixedBuffer = audioCtx.createBuffer(1, frameCount, decoded.sampleRate)
      mixedBuffer.copyToChannel(mono, 0)
    }
    source.buffer = mixedBuffer
    source.connect(offline.destination)
    source.start(0)
    const rendered = await offline.startRendering()
    const monoData = rendered.getChannelData(0)
    const wavBlob = encodeWavFromFloat32(monoData, TARGET_SAMPLE_RATE)
    console.log('[voice] Converted WebM -> WAV (client) bytes', webmBlob.size, '->', wavBlob.size)
    return wavBlob
  } catch (err) {
    console.warn('[voice] Client WAV conversion failed, falling back to raw webm', err)
    return webmBlob
  }
}

export async function voiceChat(blob, { language, sessionId } = {}) {
  // Attempt client-side conversion first
  const wavBlob = await convertWebmBlobToWav(blob)
  const isWav = wavBlob.type === 'audio/wav'
  const form = new FormData()
  form.append('file', isWav ? wavBlob : blob, isWav ? 'voice.wav' : 'voice.webm')
  if (language) form.append('language', language)
  if (sessionId) form.append('session_id', sessionId)
  const res = await fetch(`${API_BASE}/voice/chat`, { method: 'POST', body: form })
  if (!res.ok) {
    let detail = ''
    try { detail = await res.text() } catch (_) {}
    throw new Error(`voice/chat HTTP ${res.status}${detail ? ' - ' + detail : ''}`)
  }
>>>>>>> Stashed changes
  return res.json()
}

export async function sttOnly(blob) {
<<<<<<< Updated upstream
  const form = new FormData()
  form.append('file', blob, 'voice.webm')
  const res = await fetch(`${API_BASE}/voice/stt`, { method: 'POST', body: form })
  if (!res.ok) throw new Error(`voice/stt HTTP ${res.status}`)
=======
  const wavBlob = await convertWebmBlobToWav(blob)
  const isWav = wavBlob.type === 'audio/wav'
  const form = new FormData()
  form.append('file', isWav ? wavBlob : blob, isWav ? 'voice.wav' : 'voice.webm')
  const res = await fetch(`${API_BASE}/voice/stt`, { method: 'POST', body: form })
  if (!res.ok) {
    let detail = ''
    try { detail = await res.text() } catch (_) {}
    throw new Error(`voice/stt HTTP ${res.status}${detail ? ' - ' + detail : ''}`)
  }
>>>>>>> Stashed changes
  return res.json()
}

export async function tts(text) {
  const res = await fetch(`${API_BASE}/voice/tts`, { 
    method: 'POST', 
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ text }) 
  })
<<<<<<< Updated upstream
  if (!res.ok) throw new Error(`voice/tts HTTP ${res.status}`)
  return res.json()
}

export function playBase64Audio(b64) {
=======
  if (!res.ok) {
    let detail = ''
    try { detail = await res.text() } catch (_) {}
    throw new Error(`voice/tts HTTP ${res.status}${detail ? ' - ' + detail : ''}`)
  }
  return res.json()
}

export function playBase64Audio(b64, format = 'wav') {
>>>>>>> Stashed changes
  try {
    const binary = atob(b64)
    const len = binary.length
    const bytes = new Uint8Array(len)
    for (let i = 0; i < len; i++) bytes[i] = binary.charCodeAt(i)
<<<<<<< Updated upstream
    const blob = new Blob([bytes], { type: 'audio/mpeg' })
    const url = URL.createObjectURL(blob)
    const audio = new Audio(url)
    audio.play()
=======
    // Map simple format labels to MIME types; default to wav
    const mimeMap = {
      mp3: 'audio/mpeg',
      mpeg: 'audio/mpeg',
      wav: 'audio/wav',
      webm: 'audio/webm',
      ogg: 'audio/ogg'
    }
    const mime = mimeMap[(format || '').toLowerCase()] || 'audio/wav'
    const blob = new Blob([bytes], { type: mime })
    const url = URL.createObjectURL(blob)
    const audio = new Audio(url)
    audio.play().catch(err => console.warn('Autoplay blocked, user gesture needed', err))
>>>>>>> Stashed changes
    audio.onended = () => URL.revokeObjectURL(url)
  } catch (e) {
    console.error('Failed to play audio', e)
  }
}
