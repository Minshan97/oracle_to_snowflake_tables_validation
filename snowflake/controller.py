from snowflake.queries import get_rpt_data


rpt_data = get_rpt_data('2025-01-01')

print(f"DATA:\n{rpt_data}")