"""Main entry point for trash collection VRP solver."""

import argparse
import logging
import sys
from .problem.problem import ProbTrash
from .initialization.initial_solver import TruckManyVisitsDump
from .optimization.fleet_optimizer import Optimizer
from .base_classes.utils import Logger

Logger.setup_logging()
logger = logging.getLogger(__name__)


def main():
    """Main function."""
    parser = argparse.ArgumentParser(description='Trash Collection VRP Solver')
    parser.add_argument('infile', help='Input file base name (without extension)')
    parser.add_argument('--iterations', type=int, default=50, help='Number of iterations')
    parser.add_argument('--data-path', help='Path to data files')
    
    args = parser.parse_args()
    
    try:
        # Determine file path
        if args.data_path:
            infile = f"{args.data_path}/{args.infile}"
        else:
            infile = args.infile
        
        logger.info(f"Starting solver for: {infile}")
        
        # Test OSRM connection (placeholder)
        # osrmi = OsrmClient.instance()
        # osrmi.use_osrm(True)
        # test_result = osrmi.test_osrm_client(...)
        # assert test_result == True
        
        iteration = args.iterations
        best_cost = float('inf')
        best_sol = None
        
        # Initialize problem
        tp = TruckManyVisitsDump(infile)
        
        # Try different initial solution strategies
        for icase in range(1, 8):
            logger.info(f"Trying initial solution strategy: {icase}")
            tp.process(icase)
            cost = tp.get_cost_osrm()
            
            if cost < best_cost:
                logger.info(f"Strategy {icase} is best with cost: {cost}")
                best_cost = cost
                best_sol = tp.to_solution()
        
        # Optimize
        if best_sol:
            logger.info("Starting optimization...")
            opt_sol = Optimizer(best_sol, iteration)
            if opt_sol.get_cost_osrm() < best_cost:
                best_cost = opt_sol.get_cost_osrm()
                best_sol = opt_sol
        
        # Output solution
        if best_sol:
            logger.info(f"Best solution cost: {best_cost}")
            logger.info(f"Fleet size: {best_sol.get_fleet_size()}")
            logger.info(f"Pickups: {best_sol.count_pickups()}")
            
            # Save solution to file
            output_file = f"{infile}.sol.txt"
            best_sol.save_to_file(output_file)
            logger.info(f"Solution saved to: {output_file}")
            
            # Also dump to stdout for PostgreSQL format
            best_sol.dump_solution_for_pg()
        else:
            logger.error("No solution found")
            return 1
        
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())

