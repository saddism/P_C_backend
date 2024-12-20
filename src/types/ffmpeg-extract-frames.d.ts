declare module 'ffmpeg-extract-frames' {
  interface ExtractOptions {
    input: string;
    output: string;
    offsets: number[];
  }

  function extractFrames(options: ExtractOptions): Promise<void>;
  export default extractFrames;
}
