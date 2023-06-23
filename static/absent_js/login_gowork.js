// login_gowork js 코드
function gowork() {
  const empId = document.getElementById('empid').value;
  const empPhone = document.getElementById('empphone').value;
  const currentTime = new Date().toLocaleTimeString();

  fetch('/gowork/?empId=' + empId + '&empPhone=' + empPhone)
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          console.log('직원의 출근이 성공적으로 기록되었습니다.');

          alert(empId + '번 직원의 출근이 성공적으로 기록되었습니다.'+'\n 출근시간 : '+ currentTime);

        } else {
          console.error('직원정보를 찾을 수 없습니다.');
          alert('직원정보를 찾을 수 없습니다.');
        }
      })
      .catch(error => {
        console.error('오류가 발생했습니다:', error);
        alert('오류 발생');

      });
  // 입력 칸 초기화
    document.getElementById('workonoff').reset();

  return false; // 폼 제출에 의한 페이지 새로고침 방지
}
function gohome() {
  const empId = document.getElementById('empid').value;
  const empPhone = document.getElementById('empphone').value;
  const currentTime = new Date().toLocaleTimeString();


  fetch('/gohome/?empId=' + empId + '&empPhone=' + empPhone)
    .then(response => response.json())
    .then(data => {
      if (data.success) {
        console.log('직원의 퇴근이 성공적으로 기록되었습니다.');

        alert(empId+'번 직원의 퇴근이 성공적으로 기록되었습니다.'+'\n 퇴근시간 : '+ currentTime);

      } else {
        console.error('출근 기록이 없습니다.','message');
        alert('직원의 출근 기록이 없습니다.');

      }
    })
    .catch(error => {
      console.error('오류가 발생했습니다:', error);
      alert('Some Errors');
    });
  // 입력 칸 초기화
    document.getElementById('workonoff').reset();

  return false; // 폼 제출에 의한 페이지 새로고침 방지
}