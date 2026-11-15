export function RawMessage({ sample }) {
  return <pre>{JSON.stringify(sample, null, 2)}</pre>;
}

export function SampleTable({ sample }) {
  return (
    <table>
      <tbody>
        {Object.entries(sample).map(([key, value]) => (
          <tr key={key}>
            <th scope="row">{key}</th>
            <td>{JSON.stringify(value)}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

export const panels = { "Raw Messages": RawMessage, Table: SampleTable };
