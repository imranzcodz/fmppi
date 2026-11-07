export interface TableProps<T> {
  columns: { key: string; label: string }[]
  data: T[]
  renderCell?: (row: T, key: string) => React.ReactNode
  rowKey?: keyof T
}

export const Table = <T,>({
  columns,
  data,
  renderCell,
  rowKey = 'id' as keyof T,
}: TableProps<T>): React.ReactNode => (
  <div className="overflow-x-auto">
    <table className="min-w-full divide-y divide-gray-200">
      <thead className="bg-gray-50">
        <tr>
          {columns.map((col) => (
            <th key={col.key} className="px-4 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
              {col.label}
            </th>
          ))}
        </tr>
      </thead>
      <tbody className="bg-white divide-y divide-gray-200">
        {data.map((row) => (
          <tr key={String(row[rowKey])} className="hover:bg-gray-50">
            {columns.map((col) => (
              <td key={col.key} className="px-4 py-4 whitespace-nowrap text-sm text-gray-900">
                {renderCell ? renderCell(row, col.key) : String((row as Record<string, unknown>)[col.key] ?? '-')}
              </td>
            ))}
          </tr>
        ))}
        {data.length === 0 && (
          <tr>
            <td colSpan={columns.length} className="px-4 py-4 text-center text-sm text-gray-500">
              No records found
            </td>
          </tr>
        )}
      </tbody>
    </table>
  </div>
)
