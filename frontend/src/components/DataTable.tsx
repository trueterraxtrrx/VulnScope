export function DataTable<T>({
  rows,
  columns,
  empty = "No records"
}: {
  rows: T[];
  columns: { key: string; header: string; render: (row: T) => React.ReactNode }[];
  empty?: string;
}) {
  return (
    <div className="overflow-x-auto rounded-md border border-line bg-surface">
      <table className="min-w-full text-left text-sm">
        <thead className="bg-panel text-xs uppercase text-slate-400">
          <tr>
            {columns.map((column) => (
              <th key={column.key} className="whitespace-nowrap px-4 py-3 font-semibold">
                {column.header}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.length === 0 ? (
            <tr>
              <td className="px-4 py-6 text-slate-400" colSpan={columns.length}>
                {empty}
              </td>
            </tr>
          ) : (
            rows.map((row, index) => (
              <tr key={index} className="border-t border-line hover:bg-panel/60">
                {columns.map((column) => (
                  <td key={column.key} className="whitespace-nowrap px-4 py-3">
                    {column.render(row)}
                  </td>
                ))}
              </tr>
            ))
          )}
        </tbody>
      </table>
    </div>
  );
}
// Project version: VulnScope V1.4
