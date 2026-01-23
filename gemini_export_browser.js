// Gemini Gem 리서치 내용 추출 스크립트
// 브라우저 개발자 도구 콘솔에서 실행하세요

(function() {
    // 모든 텍스트 콘텐츠 추출
    const extractContent = () => {
        const content = [];

        // 제목 추출
        const title = document.querySelector('h1, [role="heading"]');
        if (title) {
            content.push('='.repeat(80));
            content.push('제목: ' + title.innerText.trim());
            content.push('='.repeat(80));
            content.push('');
        }

        // 모든 메시지/대화 콘텐츠 추출
        const messages = document.querySelectorAll('[data-test-id*="message"], .message, [class*="message"], article, [role="article"]');
        messages.forEach((msg, idx) => {
            const text = msg.innerText.trim();
            if (text && text.length > 10) { // 짧은 텍스트 필터링
                content.push(`\n--- 섹션 ${idx + 1} ---`);
                content.push(text);
                content.push('');
            }
        });

        // 특정 콘텐츠 컨테이너 추출
        const containers = document.querySelectorAll('main, [role="main"], .content, [class*="content"]');
        containers.forEach((container, idx) => {
            const paragraphs = container.querySelectorAll('p, pre, code, li');
            paragraphs.forEach((p) => {
                const text = p.innerText.trim();
                if (text && text.length > 10) {
                    content.push(text);
                    content.push('');
                }
            });
        });

        return content.filter(line => line !== undefined).join('\n');
    };

    // 콘텐츠 추출
    const fullContent = extractContent();

    // 다운로드
    const blob = new Blob([fullContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `gemini_research_${new Date().toISOString().split('T')[0]}.txt`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    console.log('✅ 다운로드 완료!');
    console.log('추출된 콘텐츠 길이:', fullContent.length, '문자');

    // 미리보기
    console.log('\n--- 미리보기 (처음 500자) ---');
    console.log(fullContent.substring(0, 500));
})();
