function openCardDetail(cardUrl) { // card 팝업창
    // const url = `mypage/card_detail/${cardId}/`; 
    window.open(cardUrl, 'CardDetail', 'width=500,height=300');
}
    
async function copyToClipboard(textToCopy) {
    try {
        await navigator.clipboard.writeText(textToCopy); // 비동기적으로 복사
        alert('키가 복사되었습니다!');
    } catch (err) {
        console.error('클립보드 복사 실패:', err);
        alert('클립보드 복사에 실패했습니다.');
    }
}