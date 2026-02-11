PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE algorithm_info (
	id INTEGER NOT NULL, 
	algo_name VARCHAR(50) NOT NULL, 
	items INTEGER NOT NULL, 
	steps INTEGER NOT NULL, 
	start_time FLOAT NOT NULL, 
	end_time FLOAT NOT NULL, 
	total_time_ms FLOAT NOT NULL, 
	time_complexity VARCHAR(50) NOT NULL, 
	path_to_graph VARCHAR(50) NOT NULL, 
	PRIMARY KEY (id)
);
INSERT INTO algorithm_info VALUES(1,'binary_search',1000,10,299407.5690775000257,299407.5692357079825,0.05601229198509827256,'O(log n)','/images/static/binary_search.png');
COMMIT;
