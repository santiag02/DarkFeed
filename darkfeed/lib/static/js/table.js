
  document.addEventListener("DOMContentLoaded", () => {
  const searchInputs = document.querySelectorAll(".search_column");
  const table = document.querySelector("#table");
  const tableRows = table.querySelectorAll("tbody tr");

  searchInputs.forEach(input => {
    input.addEventListener("input", filterTable);
  });

  function filterTable() {
    const queries = Array.from(searchInputs).map(input => input.value.toLowerCase());

    tableRows.forEach(row => {
      const cells = row.querySelectorAll("td");
      const shouldShowRow = Array.from(cells).every((cell, index) => {
        const query = queries[index] || "";
        const cellValue = cell.textContent.toLowerCase().replace(",", "");
        return cellValue.includes(query);
      });

      row.style.display = shouldShowRow ? "" : "none";
    });
  }

  document.getElementById("exportButton").addEventListener("click", () => {
    const workbook = XLSX.utils.book_new();
    const rows = Array.from(table.querySelectorAll("tr")).filter(row => {
      return row.style.display !== "none";
    }).map(row => {
      return Array.from(row.querySelectorAll("td, th")).map(cell => cell.textContent);
    });

    const worksheet = XLSX.utils.aoa_to_sheet(rows);
    XLSX.utils.book_append_sheet(workbook, worksheet, "DarkFeed");
    XLSX.writeFile(workbook, "darkfeed.xlsx");
  });
});
