// HTML 파일 내용을 클립보드에 두 가지 형식으로 넣는다.
//   - HTML 형식: 티스토리 "기본모드"에 붙여넣으면 서식이 적용된 글로 들어간다
//   - 텍스트 형식: "HTML 모드"에 붙여넣으면 소스 코드가 들어간다
// 사용법: osascript -l JavaScript tools/set_clipboard_html.js <html 파일>
ObjC.import("AppKit");

function run(argv) {
  const html = $.NSString.stringWithContentsOfFileEncodingError(argv[0], $.NSUTF8StringEncoding, null);
  if (html.isNil()) throw new Error("파일을 읽을 수 없음: " + argv[0]);
  const pb = $.NSPasteboard.generalPasteboard;
  pb.clearContents;
  pb.setStringForType(html, $.NSPasteboardTypeHTML);
  pb.setStringForType(html, $.NSPasteboardTypeString);
}
