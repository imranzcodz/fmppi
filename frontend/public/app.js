(function () {
  const container = document.getElementById("app");
  const caseCount = document.createElement("p");
  caseCount.id = "case-count";
  caseCount.textContent = "Cases: 0";
  container.appendChild(caseCount);

  window.fmppi = {
    setCaseCount: function (n) {
      caseCount.textContent = "Cases: " + n;
    },
  };
})();
