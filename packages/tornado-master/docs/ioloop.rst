``tornado.ioloop`` --- Main event loop
======================================

.. automodule:: tornado.ioloop

   IOLoop objects
   --------------

   .. autoclass:: IOLoop

   Running an IOLoop
   ^^^^^^^^^^^^^^^^^

   .. automethod:: IOLoop.current
   .. automethod:: IOLoop.make_current
   .. automethod:: IOLoop.clear_current
   .. automethod:: IOLoop.start
   .. automethod:: IOLoop.stop
   .. automethod:: IOLoop.run_sync
   .. automethod:: IOLoop.close
   .. automethod:: IOLoop.instance
   .. automethod:: IOLoop.install
   .. automethod:: IOLoop.clear_instance

   I/O events
   ^^^^^^^^^^

   .. automethod:: IOLoop.add_handler
   .. automethod:: IOLoop.update_handler
   .. automethod:: IOLoop.remove_handler

   Callbacks and timeouts
   ^^^^^^^^^^^^^^^^^^^^^^

   .. automethod:: IOLoop.add_callback
   .. automethod:: IOLoop.add_callback_from_signal
   .. automethod:: IOLoop.add_future
   .. automethod:: IOLoop.add_timeout
   .. automethod:: IOLoop.call_at
   .. automethod:: IOLoop.call_later
   .. automethod:: IOLoop.remove_timeout
   .. automethod:: IOLoop.spawn_callback
   .. automethod:: IOLoop.run_in_executor
   .. automethod:: IOLoop.set_default_executor
   .. automethod:: IOLoop.time
   .. autoclass:: PeriodicCallback
      :members:
