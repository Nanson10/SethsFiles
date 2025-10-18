import pstats

# 2. Load the stats file into a Stats object
stats = pstats.Stats('profile_results.prof')

# 3. Clean up the file paths for readability
stats.strip_dirs()

# 4. Sort the statistics by cumulative time
stats.sort_stats(pstats.SortKey.CUMULATIVE)

# 5. Print the top 10 most expensive functions
stats.print_stats(10)

# 6. Print the callers of a specific function
stats.print_callers('function_name_to_investigate')